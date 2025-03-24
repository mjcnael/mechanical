import { apiInstance } from "@/shared/api/api-instance";
import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
} from "@tanstack/react-table";

import { MoreHorizontal } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/ui/default/table";
import { Button } from "@/shared/ui/default/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/default/dropdown-menu";
import { Dialog, DialogContent, DialogTitle } from "@/shared/ui/default/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/default/form";
import { Input } from "@/shared/ui/default/input";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Textarea } from "@/shared/ui/default/textarea";
import { DateTime } from "luxon";
import {
  dateTimeFormat,
  fetchForemen,
  fetchTechnicians,
} from "@/pages/foremen-page";
import { TechnicianDto } from "./technicians-table";
import { ForemanDto } from "./foremen-table";
import { useParams } from "react-router-dom";

async function fetchTasks() {
  const { data } = await apiInstance.get("/technician-tasks");
  return data;
}

export const fetchTechnicianTasks = async (technicianId: string) => {
  const { data } = await apiInstance.get(`/technicians/${technicianId}/tasks`);
  return data;
};

const updateTaskStatus = async (taskId: number, status: string) => {
  await apiInstance.post("/technician-tasks/status", {
    task_id: taskId,
    status: status,
  });
};

export type TaskUpdateDto = {
  start_time: string;
  end_time: string;
  task_description: string;
};

async function updateTask(task_id: number, task: TaskUpdateDto) {
  return await apiInstance.put(`/technician-tasks/${task_id}`, task);
}

export type TaskDto = {
  task_id: number;
  start_time: string;
  end_time: string;
  workshop: string;
  foreman_id: number;
  technician_id: number;
  task_description: string;
  status: string;
};

const FormSchema = z
  .object({
    start_time: z
      .string()
      .refine(
        (value) => DateTime.fromFormat(value, dateTimeFormat).isValid,
        "Неверный формат даты и времени (ДД.ММ.ГГГГ ЧЧ:ММ)",
      ),
    end_time: z
      .string()
      .refine(
        (value) => DateTime.fromFormat(value, dateTimeFormat).isValid,
        "Неверный формат даты и времени (ДД.ММ.ГГГГ ЧЧ:ММ)",
      ),
    task_description: z.coerce.string().max(500).min(5),
  })
  .refine(
    (data) => {
      const start = DateTime.fromFormat(data.start_time, dateTimeFormat);
      const end = DateTime.fromFormat(data.end_time, dateTimeFormat);
      return end > start;
    },
    {
      message: "Время окончания должно быть позже времени начала",
      path: ["end_time"],
    },
  );

type TasksTableProps = {
  editable?: boolean;
};

const TasksTable = (props: TasksTableProps) => {
  const { id } = useParams();

  const query_fn = props.editable
    ? fetchTasks
    : () => fetchTechnicianTasks(id!);

  const { data = [], isLoading } = useQuery("technician-tasks", query_fn);

  const { data: foremenData = [], isLoading: isForemanLoading } = useQuery(
    "foremen",
    fetchForemen,
  );
  const { data: techniciansData = [], isLoading: isTechnicianLoading } =
    useQuery("technicians", fetchTechnicians);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [updateRow, setUpdateRow] = useState<TaskDto>();
  const queryClient = useQueryClient();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {},
  });

  const taskUpdateMutation = useMutation(
    ({ task_id, newTask }: { task_id: number; newTask: TaskUpdateDto }) =>
      updateTask(task_id, newTask),
    {
      onSuccess: () => {
        toast.success(`Задача ${updateRow?.task_id} успешно обновлена`);
        queryClient.invalidateQueries(["technician-tasks"]);
      },
    },
  );

  const taskUpdateStatusMutation = useMutation(
    ({ task_id, status }: { task_id: number; status: string }) =>
      updateTaskStatus(task_id, status),
    {
      onSuccess: (_data, variables) => {
        console.log(updateRow);
        if (variables.status === "Выполнено") {
          toast.success(`Задача ${variables.task_id} успешно выполнена`);
        }
        if (variables.status === "Отменено") {
          toast.success(`Задача ${variables.task_id} успешно отменена`);
        }
        queryClient.invalidateQueries(["technician-tasks"]);
      },
    },
  );

  const onTaskUpdate = (task: TaskUpdateDto) => {
    if (updateRow?.task_id) {
      taskUpdateMutation.mutate({
        task_id: updateRow.task_id,
        newTask: task,
      });
      setIsDialogOpen(false);
    }
  };

  const columns: ColumnDef<TaskDto>[] = [
    {
      accessorKey: "task_id",
      header: "Номер задачи",
      size: 90,
    },
    {
      accessorKey: "start_time",
      header: "Начало",
    },
    {
      accessorKey: "end_time",
      header: "Окончание",
    },
    {
      accessorKey: "workshop",
      header: "Цех",
    },
    {
      accessorKey: "foreman_id",
      header: "Начальник",
      cell: ({ row }) => {
        const [isForemanOpen, setIsForemanOpen] = useState(false);

        const foreman: ForemanDto = foremenData.find(
          (value: ForemanDto) =>
            value.foreman_id === row.getValue("foreman_id"),
        );

        if (!foreman) return <></>;

        return (
          <div>
            <span
              onClick={() => setIsForemanOpen(true)}
              className="cursor-pointer text-emerald-400 hover:underline"
            >
              {foreman.full_name}
            </span>

            <Dialog open={isForemanOpen} onOpenChange={setIsForemanOpen}>
              <DialogContent aria-describedby={undefined}>
                <DialogTitle>Карточка начальника</DialogTitle>
                <div className="space-y-2">
                  <p>Табельный номер: {foreman.foreman_id}</p>
                  <p>ФИО: {foreman.full_name}</p>
                  <p>Пол: {foreman.gender}</p>
                  <p>Цеx: {foreman.workshop}</p>
                  <p>Телефон: {foreman.phone_number}</p>
                </div>
                <Button
                  onClick={() => setIsForemanOpen(false)}
                  className="mt-4"
                >
                  Закрыть
                </Button>
              </DialogContent>
            </Dialog>
          </div>
        );
      },
    },
    {
      accessorKey: "task_description",
      header: "Описание",
      cell: ({ row }) => {
        const [isDescOpen, setIsDescOpen] = useState(false);
        const fullDescription: string = row.getValue("task_description");
        const shortDescription =
          fullDescription.length > 20
            ? `${fullDescription.substring(0, 20)}...`
            : fullDescription;

        return (
          <div>
            <span
              onClick={() => setIsDescOpen(true)}
              className="cursor-pointer text-blue-400 hover:underline"
            >
              {shortDescription}
            </span>

            <Dialog open={isDescOpen} onOpenChange={setIsDescOpen}>
              <DialogContent aria-describedby={undefined}>
                <DialogTitle>Описание задачи</DialogTitle>
                <p>{fullDescription}</p>
                <Button onClick={() => setIsDescOpen(false)} className="mt-4">
                  Закрыть
                </Button>
              </DialogContent>
            </Dialog>
          </div>
        );
      },
    },
    {
      accessorKey: "status",
      header: "Статус",
    },
    {
      id: "actions",
      size: 35,
      cell: ({ row }) => {
        const task: TaskDto = {
          task_id: row.getValue("task_id"),
          start_time: row.getValue("start_time"),
          end_time: row.getValue("end_time"),
          workshop: row.getValue("workshop"),
          foreman_id: props.editable ? row.getValue("foreman_id") : 0,
          technician_id: props.editable ? row.getValue("technician_id") : 0,
          task_description: row.getValue("task_description"),
          status: row.getValue("status"),
        };

        const isEditable = task.status === "Не выполнено";

        return (
          <DropdownMenu>
            <div className={!isEditable ? "hover:cursor-not-allowed" : ""}>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="h-8 w-8 p-0"
                  disabled={!isEditable}
                >
                  <MoreHorizontal />
                </Button>
              </DropdownMenuTrigger>
            </div>
            <DropdownMenuContent align="end">
              {props.editable ? (
                <>
                  <DropdownMenuGroup>
                    <DropdownMenuItem
                      onClick={() => {
                        setUpdateRow(task);
                        form.reset(task);
                        setIsDialogOpen(true);
                      }}
                    >
                      Редактировать
                    </DropdownMenuItem>
                  </DropdownMenuGroup>
                  <DropdownMenuSeparator />
                </>
              ) : (
                <></>
              )}
              <DropdownMenuGroup>
                <DropdownMenuItem
                  onClick={() => {
                    setUpdateRow(task);
                    taskUpdateStatusMutation.mutate({
                      task_id: task.task_id,
                      status: "Выполнено",
                    });
                  }}
                >
                  Выполнить
                </DropdownMenuItem>

                {props.editable ? (
                  <DropdownMenuItem
                    onClick={() => {
                      setUpdateRow(task);
                      taskUpdateStatusMutation.mutate({
                        task_id: task.task_id,
                        status: "Отменено",
                      });
                    }}
                  >
                    Отменить
                  </DropdownMenuItem>
                ) : (
                  <></>
                )}
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  if (isLoading || isTechnicianLoading || isForemanLoading) {
    return <h3>Загрузка...</h3>;
  }

  if (props.editable) {
    columns.splice(5, 0, {
      accessorKey: "technician_id",
      header: "Работник",
      size: 150,
      cell: ({ row }) => {
        const [isTechnicianOpen, setIsTechnicianOpen] = useState(false);

        const technician: TechnicianDto = techniciansData.find(
          (value: TechnicianDto) =>
            value.technician_id === row.getValue("technician_id"),
        );

        if (!technician) return <></>;

        return (
          <div>
            <span
              onClick={() => setIsTechnicianOpen(true)}
              className="cursor-pointer text-amber-400 hover:underline"
            >
              {technician.full_name}
            </span>

            <Dialog open={isTechnicianOpen} onOpenChange={setIsTechnicianOpen}>
              <DialogContent aria-describedby={undefined}>
                <DialogTitle>Карточка технического работника</DialogTitle>
                <div className="space-y-2">
                  <p>Табельный номер: {technician.technician_id}</p>
                  <p>ФИО: {technician.full_name}</p>
                  <p>Пол: {technician.gender}</p>
                  <p>Специализация: {technician.specialization}</p>
                  <p>Телефон: {technician.phone_number}</p>
                </div>
                <Button
                  onClick={() => setIsTechnicianOpen(false)}
                  className="mt-4"
                >
                  Закрыть
                </Button>
              </DialogContent>
            </Dialog>
          </div>
        );
      },
    });
  }

  return (
    <div className="w-full">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    style={{
                      minWidth: header.column.columnDef.size,
                      maxWidth: header.column.columnDef.size,
                    }}
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext(),
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell
                      key={cell.id}
                      style={{
                        minWidth: cell.column.columnDef.size,
                        maxWidth: cell.column.columnDef.size,
                      }}
                      className={
                        cell.column.id == "actions" ? "text-right" : ""
                      }
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="text-center">
                  Пусто
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent aria-describedby={undefined}>
          <DialogTitle>Редактировать задачу</DialogTitle>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onTaskUpdate)}>
              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="start_time"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Дата и время окончания</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          placeholder="ДД.ММ.ГГГГ ЧЧ:ММ"
                          {...field}
                          required
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="end_time"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Дата и время окончания</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          placeholder="ДД.ММ.ГГГГ ЧЧ:ММ"
                          {...field}
                          required
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="task_description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Описание</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Добавьте описание"
                          className="resize-none h-[200px]"
                          required
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <Button type="submit" className="mt-4">
                Обновить
              </Button>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TasksTable;
