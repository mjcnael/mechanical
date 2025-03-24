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
  DropdownMenuItem,
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

async function fetchTechnicans() {
  const { data } = await apiInstance.get("/technicians");
  return data;
}

export type TechnicianUpdateDto = {
  full_name: string;
  specialization: string;
  phone_number: string;
};

async function updateTechnician(
  technician_id: number,
  technician: TechnicianUpdateDto,
) {
  return await apiInstance.put(`/technicians/${technician_id}`, technician);
}

export type TechnicianDto = {
  technician_id: number;
  full_name: string;
  gender: string;
  specialization: string;
  phone_number: string;
};

const FormSchema = z.object({
  full_name: z
    .string()
    .regex(
      /^\S+ \S+ \S+$/,
      "ФИО должно содержать фамилию, имя и отчество разделенные пробелом",
    ),
  specialization: z
    .string()
    .max(50, "Специализация должна содержать не более 50 символов"),
  phone_number: z
    .string()
    .regex(/^\+?\d{11}$/, "Введите корректный номер телефона"),
});

const TechniciansTable = () => {
  const { data = [], isLoading } = useQuery("technicians", fetchTechnicans);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [updateRow, setUpdateRow] = useState<TechnicianDto>();
  const queryClient = useQueryClient();

  const form = useForm({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      full_name: "",
      specialization: "",
      phone_number: "",
    },
  });

  const technicianUpdateMutation = useMutation(
    ({
      technician_id,
      newTechnician,
    }: {
      technician_id: number;
      newTechnician: TechnicianUpdateDto;
    }) => updateTechnician(technician_id, newTechnician),
    {
      onSuccess: () => {
        toast.success(
          `Технический работник ${updateRow?.technician_id} успешно обновлен`,
        );
        queryClient.invalidateQueries(["technicians"]);
        setIsDialogOpen(false);
      },
      onError: (e) => {
        toast.error(`Error: ${e.response.data?.detail}`);
      },
    },
  );

  const onTechnicanUpdate = (technician: TechnicianUpdateDto) => {
    if (updateRow?.technician_id) {
      technicianUpdateMutation.mutate({
        technician_id: updateRow.technician_id,
        newTechnician: technician,
      });
    }
  };

  const columns: ColumnDef<TechnicianDto>[] = [
    {
      accessorKey: "technician_id",
      header: "Табельный номер",
      size: 100,
    },
    {
      accessorKey: "full_name",
      header: "ФИО",
    },
    {
      accessorKey: "gender",
      header: "Пол",
      size: 50,
    },
    {
      accessorKey: "specialization",
      header: "Специализация",
    },
    {
      accessorKey: "phone_number",
      header: "Номер телефона",
    },
    {
      id: "actions",
      size: 40,
      cell: ({ row }) => {
        const technician: TechnicianDto = {
          technician_id: row.getValue("technician_id"),
          full_name: row.getValue("full_name"),
          gender: row.getValue("gender"),
          specialization: row.getValue("specialization"),
          phone_number: row.getValue("phone_number"),
        };

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <MoreHorizontal />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => {
                  setUpdateRow(technician);
                  form.reset(technician);
                  setIsDialogOpen(true);
                }}
              >
                Редактировать
              </DropdownMenuItem>
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

  if (isLoading) {
    return <h3>Loading...</h3>;
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
          <DialogTitle>Редактировать технического работника</DialogTitle>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onTechnicanUpdate)}>
              <div className="space-y-2">
                <FormField
                  control={form.control}
                  name="full_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>ФИО</FormLabel>
                      <FormControl>
                        <Input {...field} required />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="specialization"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Специализация</FormLabel>
                      <FormControl>
                        <Input {...field} required />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="phone_number"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Номер телефона</FormLabel>
                      <FormControl>
                        <Input {...field} required />
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

export default TechniciansTable;
