import ForemenTable, { ForemanDto } from "@/features/foremen-table";
import TechniciansTable, { TechnicianDto } from "@/features/technicians-table";
import { apiInstance } from "@/shared/api/api-instance";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/ui/default/button";
import { Card, CardContent, CardHeader } from "@/shared/ui/default/card";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/ui/default/command";
import { DialogContent, DialogTitle } from "@/shared/ui/default/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/default/form";
import { Input } from "@/shared/ui/default/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/shared/ui/default/popover";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/shared/ui/default/tabs";
import { Textarea } from "@/shared/ui/default/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import { Dialog } from "@radix-ui/react-dialog";
import { Check, ChevronsUpDown, Funnel } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { toast } from "sonner";
import { z } from "zod";
import { DateTime } from "luxon";
import TasksTable from "@/features/tasks-table";
import formatDateToInput from "@/utils/formatDateToInput.tsx";
import { Checkbox } from "@/shared/ui/default/checkbox";
export const dateTimeFormat = "dd.MM.yyyy HH:mm";

export type ForemanCreateDto = {
  full_name: string;
  gender: string;
  workshop: string;
  phone_number: string;
};

export type TechnicianCreateDto = {
  specialization: string;
  full_name: string;
  gender: string;
  phone_number: string;
};

export type TaskCreateDto = {
  start_time: string;
  end_time: string;
  workshop: number;
  foreman_id: number;
  technician_id: number;
  task_description: string;
  important: boolean;
};

export type FilterDto = {
  date_start: string;
  date_end: string;
  workshop: string;
  foreman_name: string;
  technician_name: string;
  status: string;
};

export async function fetchForemen() {
  const { data } = await apiInstance.get("/foremen");
  return data;
}

export async function fetchTechnicians() {
  const { data } = await apiInstance.get("/technicians");
  return data;
}

async function createForeman(foreman: ForemanCreateDto) {
  return await apiInstance.post("/foremen", foreman);
}

async function createTechnician(technician: TechnicianCreateDto) {
  return await apiInstance.post("/technicians", technician);
}

async function createTask(task: TaskCreateDto) {
  return await apiInstance.post("/technician-tasks", task);
}

const ForemanFormSchema = z.object({
  full_name: z
    .string()
    .regex(
      /^\S+ \S+ \S+$/,
      "ФИО должно содержать фамилию, имя и отчество разделенные пробелом",
    ),
  gender: z.enum(["М", "Ж"], { message: "Выберите корректный пол" }),
  workshop: z
    .string()
    .max(50, "Название цеха должно содержать не более 50 символов"),
  phone_number: z
    .string()
    .regex(/^\+?\d{11}$/, "Введите корректный номер телефона"),
});

const TechnicianFormSchema = z.object({
  full_name: z
    .string()
    .regex(
      /^\S+ \S+ \S+$/,
      "ФИО должно содержать фамилию, имя и отчество разделенные пробелом",
    ),
  gender: z.enum(["М", "Ж"], { message: "Выберите корректный пол" }),
  specialization: z
    .string()
    .max(50, "Специализация должна содержать не более 50 символов"),
  phone_number: z
    .string()
    .regex(/^\+?\d{11}$/, "Введите корректный номер телефона"),
});

const TaskFormSchema = z
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
    workshop: z.coerce.number().int(),
    important: z.coerce.boolean(),
    foreman_id: z.coerce.number().int(),
    technician_id: z.coerce.number().int(),
    task_description: z.coerce
      .string()
      .min(5, "Описание задачи должно содержать не менее 5 символов")
      .max(500, "Описание задачи должно содержать не более 500 символов"),
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

const FilterTaskSchema = z.object({
  date_start: z.coerce
    .string()
    .refine(
      (value) =>
        DateTime.fromFormat(value, dateTimeFormat).isValid || value == "",
      "Неверный формат даты и времени (ДД.ММ.ГГГГ ЧЧ:ММ)",
    ),
  date_end: z.coerce
    .string()
    .refine(
      (value) =>
        DateTime.fromFormat(value, dateTimeFormat).isValid || value == "",
      "Неверный формат даты и времени (ДД.ММ.ГГГГ ЧЧ:ММ)",
    ),
  workshop: z.coerce
    .string()
    .max(100, "Название цеха не должно быть длинее 100 символов"),
  technician_name: z.coerce
    .string()
    .max(50, "ФИО рабочего не должно быть длинее 50 символов"),
  foreman_name: z.coerce
    .string()
    .max(50, "ФИО начальника не должно быть длинее 50 символов"),
  status: z.coerce.string(),
});

const ForemenPage = () => {
  const { data: foremenData = [], isLoading: isForemenLoading } = useQuery(
    "foremen",
    fetchForemen,
  );
  const { data: techniciansData = [], isLoading: isTechniciansLoading } =
    useQuery("technicians", fetchTechnicians);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isFilterDialogOpen, setIsFilterDialogOpen] = useState(false);
  const [openForemen, setOpenForemen] = useState(false);
  const [openTechnicians, setOpenTechnicians] = useState(false);
  const [openWorkshop, setOpenWorkshop] = useState(false);
  const [filterData, setFilterData] = useState({
    date_start: "",
    date_end: "",
    workshop: "",
    foreman_name: "",
    technician_name: "",
    status: "",
  });

  const queryClient = useQueryClient();

  const foremanCreateMutation = useMutation(
    (newForeman: ForemanCreateDto) => createForeman(newForeman),
    {
      onSuccess: (data) => {
        toast.success(
          `Начальник цеха ${data.data.foreman_id} успешно добавлен`,
        );
        queryClient.invalidateQueries(["foremen"]);
        setIsDialogOpen(false);
      },
      onError: (e) => {
        toast.error(`Error: ${e.response.data?.detail}`);
      },
    },
  );

  const technicianCreateMutation = useMutation(
    (newTechnician: TechnicianCreateDto) => createTechnician(newTechnician),
    {
      onSuccess: (data) => {
        toast.success(
          `Технический работник ${data.data.technician_id} успешно добавлен`,
        );
        queryClient.invalidateQueries(["technicians"]);
        setIsDialogOpen(false);
      },
      onError: (e) => {
        toast.error(`Error: ${e.response.data?.detail}`);
      },
    },
  );

  const taskCreateMutation = useMutation(
    (newTask: TaskCreateDto) => createTask(newTask),
    {
      onSuccess: (data) => {
        toast.success(`Задача ${data.data.task_id} успешно добавлена`);
        queryClient.invalidateQueries(["technician-tasks"]);
        setIsDialogOpen(false);
      },
      onError: (e) => {
        toast.error(`Error: ${e.response.data?.detail}`);
      },
    },
  );

  const foreman_form = useForm({
    resolver: zodResolver(ForemanFormSchema),
    defaultValues: {
      full_name: "",
      gender: "",
      workshop: "",
      phone_number: "",
    },
  });

  const technician_form = useForm({
    resolver: zodResolver(TechnicianFormSchema),
    defaultValues: {
      specialization: "",
      full_name: "",
      gender: "",
      phone_number: "",
    },
  });

  const task_form = useForm<z.infer<typeof TaskFormSchema>>({
    resolver: zodResolver(TaskFormSchema),
    defaultValues: {
      start_time: formatDateToInput(new Date()),
      end_time: formatDateToInput(new Date()),
      important: false,
    },
  });

  const filter_form = useForm<z.infer<typeof FilterTaskSchema>>({
    resolver: zodResolver(FilterTaskSchema),
    defaultValues: {
      date_start: "",
      date_end: "",
      workshop: "",
      status: "",
      technician_name: "",
      foreman_name: "",
    },
  });
  const onForemanCreate = (foreman: ForemanCreateDto) => {
    foremanCreateMutation.mutate(foreman);
  };

  const onTechnicianCreate = (technician: TechnicianCreateDto) => {
    technicianCreateMutation.mutate(technician);
  };

  const onTaskCreate = (task: TaskCreateDto) => {

    taskCreateMutation.mutate(task);
  };

  const onFilterApplied = (filter: FilterDto) => {
    setFilterData({ ...filter });
    setIsFilterDialogOpen(false);
  };

  const resetFilterForm = () => {
    filter_form.reset();
    setFilterData(filter_form.getValues());
  };

  return (
    <div className="p-6">
      <Card className="w-full">
        <Tabs defaultValue="foremen" className="w-full">
          <CardHeader className="flex-row items-center justify-between pb-2">
            <h1 className="text-xl font-bold">Начальник Цеха</h1>
            <TabsList>
              <TabsTrigger value="foremen">Начальники цехов</TabsTrigger>
              <TabsTrigger value="technicians">
                Технические работники
              </TabsTrigger>
              <TabsTrigger value="tasks">Задачи</TabsTrigger>
            </TabsList>
          </CardHeader>
          <CardContent>
            <TabsContent value="tasks">
              <div className="flex mb-4 justify-between">
                <div>
                  <Button
                    variant="outline"
                    onClick={() => setIsDialogOpen(true)}
                  >
                    Добавить задачу
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={resetFilterForm}
                    className="underline"
                    variant="ghost"
                  >
                    Сбросить фильтры
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setIsFilterDialogOpen(true)}
                  >
                    <Funnel className="text-primary" />
                  </Button>
                </div>
              </div>

              {/*Диалоговое окно для фильтров*/}
              <Dialog
                open={isFilterDialogOpen}
                onOpenChange={setIsFilterDialogOpen}
              >
                <DialogContent aria-describedby={undefined}>
                  <DialogTitle>Фильтры</DialogTitle>
                  <Form {...filter_form}>
                    <form onSubmit={filter_form.handleSubmit(onFilterApplied)}>
                      <div className="space-y-2">
                        <div className="flex justify-between gap-3">
                          <FormField
                            control={filter_form.control}
                            name="date_start"
                            render={({ field }) => (
                              <FormItem className="w-full">
                                <FormLabel>Дата начала от</FormLabel>
                                <FormControl>
                                  <Input
                                    type="text"
                                    placeholder="19.02.2025 19:00"
                                    {...field}
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          <FormField
                            control={filter_form.control}
                            name="date_end"
                            render={({ field }) => (
                              <FormItem className="w-full">
                                <FormLabel>Дата начала до</FormLabel>
                                <FormControl>
                                  <Input
                                    type="text"
                                    placeholder="20.02.2025 20:00"
                                    {...field}
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>
                        <FormField
                          control={filter_form.control}
                          name="workshop"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Название цеха</FormLabel>
                              <FormControl>
                                <Input
                                  type="text"
                                  placeholder="Сталелитейный"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={filter_form.control}
                          name="technician_name"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Работник</FormLabel>
                              <FormControl>
                                <Input
                                  type="text"
                                  placeholder="Фамилия Имя Отчество"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={filter_form.control}
                          name="foreman_name"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Начальник цеха</FormLabel>
                              <FormControl>
                                <Input
                                  type="text"
                                  placeholder="Фамилия Имя Отчество"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={filter_form.control}
                          name="status"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Статус</FormLabel>
                              <FormControl>
                                <Input
                                  type="text"
                                  placeholder="Выполнено"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>

                      <Button type="submit" className="mt-4">
                        Применить
                      </Button>
                    </form>
                  </Form>
                </DialogContent>
              </Dialog>

              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent
                  aria-describedby={undefined}
                  className="min-w-[80%]"
                >
                  <DialogTitle>Добавить задачу</DialogTitle>
                  <Form {...task_form}>
                    <form onSubmit={task_form.handleSubmit(onTaskCreate)}>
                      <div className="space-y-2">
                        <FormField
                          control={task_form.control}
                          name="start_time"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Дата и время начала</FormLabel>
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
                          control={task_form.control}
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
                          control={task_form.control}
                          name="workshop"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Цех</FormLabel>
                              <Popover
                                open={openWorkshop}
                                onOpenChange={setOpenWorkshop}
                              >
                                <PopoverTrigger asChild>
                                  <FormControl>
                                    <Button
                                      variant="outline"
                                      role="combobox"
                                      className={cn(
                                        "w-full justify-between",
                                        !field.value && "text-muted-foreground",
                                      )}
                                    >
                                      {field.value ? (
                                        <>
                                          {foremenData.map(
                                            (foreman: ForemanDto) => {
                                              if (
                                                foreman.foreman_id ===
                                                field.value
                                              ) {
                                                return foreman.workshop;
                                              }
                                            },
                                          )}
                                        </>
                                      ) : (
                                        "Выберите цех"
                                      )}
                                      <ChevronsUpDown className="opacity-50" />
                                    </Button>
                                  </FormControl>
                                </PopoverTrigger>
                                <PopoverContent className="w-[465px] p-0">
                                  <Command>
                                    <CommandInput
                                      placeholder="Поиск..."
                                      className="h-9"
                                    />
                                    <CommandList>
                                      <CommandEmpty>Пусто</CommandEmpty>
                                      <CommandGroup>
                                        {foremenData
                                          .filter(
                                            (foreman: ForemanDto) =>
                                              foreman.workshop !== "",
                                          )
                                          .map((foreman: ForemanDto) => (
                                            <CommandItem
                                              value={`${foreman.workshop}${foreman.foreman_id}${foreman.full_name}`}
                                              key={`${foreman.foreman_id}-w`}
                                              onSelect={() => {
                                                task_form.setValue(
                                                  "workshop",
                                                  foreman.foreman_id,
                                                );
                                                setOpenWorkshop(false);
                                              }}
                                            >
                                              <div className="flex items-center space-x-1">
                                                <span>{foreman.workshop}</span>
                                                <span>
                                                  ({foreman.foreman_id}
                                                </span>
                                                <span>
                                                  <span className="text-cyan-400">{` ${foreman.full_name}`}</span>
                                                  )
                                                </span>
                                              </div>
                                              <Check
                                                className={cn(
                                                  "ml-auto",
                                                  foreman.foreman_id ===
                                                    field.value
                                                    ? "opacity-100"
                                                    : "opacity-0",
                                                )}
                                              />
                                            </CommandItem>
                                          ))}
                                      </CommandGroup>
                                    </CommandList>
                                  </Command>
                                </PopoverContent>
                              </Popover>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={task_form.control}
                          name="foreman_id"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Начальник цеха</FormLabel>
                              <Popover
                                open={openForemen}
                                onOpenChange={setOpenForemen}
                              >
                                <PopoverTrigger asChild>
                                  <FormControl>
                                    <Button
                                      variant="outline"
                                      role="combobox"
                                      className={cn(
                                        "w-full justify-between",
                                        !field.value && "text-muted-foreground",
                                      )}
                                    >
                                      {field.value ? (
                                        <>
                                          {foremenData.map(
                                            (foreman: ForemanDto) => {
                                              if (
                                                foreman.foreman_id ===
                                                field.value
                                              ) {
                                                return (
                                                  <div
                                                    key={foreman.foreman_id}
                                                    className="flex gap-2"
                                                  >
                                                    {foreman.foreman_id}
                                                    <p className="text-emerald-400">
                                                      {foreman.full_name}
                                                    </p>
                                                    <span>
                                                      {foreman.workshop}
                                                    </span>
                                                  </div>
                                                );
                                              }
                                            },
                                          )}
                                        </>
                                      ) : (
                                        "Выберите начальника цеха"
                                      )}
                                      <ChevronsUpDown className="opacity-50" />
                                    </Button>
                                  </FormControl>
                                </PopoverTrigger>
                                <PopoverContent className="w-[1076px] p-0">
                                  <Command>
                                    <CommandInput
                                      placeholder="Поиск..."
                                      className="h-9"
                                    />
                                    <CommandList>
                                      <CommandEmpty>Пусто</CommandEmpty>

                                      <CommandGroup>
                                        {foremenData
                                          .filter(
                                            (foreman: ForemanDto) =>
                                              foreman.workshop !== "",
                                          )
                                          .map((foreman: ForemanDto) => (
                                            <CommandItem
                                              value={`${foreman.foreman_id} ${foreman.full_name} ${foreman.workshop}`}
                                              key={foreman.foreman_id}
                                              onSelect={() => {
                                                task_form.setValue(
                                                  "foreman_id",
                                                  foreman.foreman_id,
                                                );
                                                setOpenForemen(false);
                                              }}
                                            >
                                              {foreman.foreman_id}
                                              <p className="text-emerald-400">
                                                {foreman.full_name}
                                              </p>
                                              {foreman.workshop}
                                              <Check
                                                className={cn(
                                                  "ml-auto",
                                                  foreman.foreman_id ===
                                                    field.value
                                                    ? "opacity-100"
                                                    : "opacity-0",
                                                )}
                                              />
                                            </CommandItem>
                                          ))}
                                      </CommandGroup>
                                    </CommandList>
                                  </Command>
                                </PopoverContent>
                              </Popover>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={task_form.control}
                          name="technician_id"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Технический работник</FormLabel>
                              <Popover
                                open={openTechnicians}
                                onOpenChange={setOpenTechnicians}
                              >
                                <PopoverTrigger asChild>
                                  <FormControl>
                                    <Button
                                      variant="outline"
                                      role="combobox"
                                      className={cn(
                                        "w-full justify-between",
                                        !field.value && "text-muted-foreground",
                                      )}
                                    >
                                      {field.value ? (
                                        <>
                                          {techniciansData.map(
                                            (technician: TechnicianDto) => {
                                              if (
                                                technician.technician_id ===
                                                field.value
                                              ) {
                                                return (
                                                  <div
                                                    key={
                                                      technician.technician_id
                                                    }
                                                    className="flex gap-2"
                                                  >
                                                    {technician.technician_id}
                                                    <p className="text-amber-400">
                                                      {technician.full_name}
                                                    </p>
                                                    <span>
                                                      {
                                                        technician.specialization
                                                      }
                                                    </span>
                                                  </div>
                                                );
                                              }
                                            },
                                          )}
                                        </>
                                      ) : (
                                        "Выберите технического работника"
                                      )}
                                      <ChevronsUpDown className="opacity-50" />
                                    </Button>
                                  </FormControl>
                                </PopoverTrigger>
                                <PopoverContent className="w-[1076px] p-0">
                                  <Command>
                                    <CommandInput
                                      placeholder="Поиск..."
                                      className="h-9"
                                    />
                                    <CommandList>
                                      <CommandEmpty>Пусто</CommandEmpty>
                                      <CommandGroup>
                                        {techniciansData.map(
                                          (technician: TechnicianDto) => (
                                            <CommandItem
                                              value={`${technician.technician_id} ${technician.full_name} ${technician.specialization}`}
                                              key={technician.technician_id}
                                              onSelect={() => {
                                                task_form.setValue(
                                                  "technician_id",
                                                  technician.technician_id,
                                                );
                                                setOpenTechnicians(false);
                                              }}
                                            >
                                              {technician.technician_id}
                                              <p className="text-amber-400">
                                                {technician.full_name}
                                              </p>
                                              {technician.specialization}
                                              <Check
                                                className={cn(
                                                  "ml-auto",
                                                  technician.technician_id ===
                                                    field.value
                                                    ? "opacity-100"
                                                    : "opacity-0",
                                                )}
                                              />
                                            </CommandItem>
                                          ),
                                        )}
                                      </CommandGroup>
                                    </CommandList>
                                  </Command>
                                </PopoverContent>
                              </Popover>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={task_form.control}
                          name="task_description"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Описание</FormLabel>
                              <FormControl>
                                <Textarea
                                  required
                                  placeholder="Добавьте описание"
                                  className="resize-none"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={task_form.control}
                          name="important"
                          render={({ field }) => (
                            <FormItem className="flex flex-row items-center gap-2">
                              <FormControl>
                                <Checkbox
                                  checked={field.value}
                                  onCheckedChange={(checked) =>
                                    field.onChange(!!checked)
                                  }
                                />
                              </FormControl>
                              <FormLabel>Важно</FormLabel>
                            </FormItem>
                          )}
                        />
                      </div>
                      <Button type="submit" className="mt-4">
                        Добавить
                      </Button>
                    </form>
                  </Form>
                </DialogContent>
              </Dialog>

              <TasksTable filter={filterData} editable />
            </TabsContent>

            <TabsContent value="foremen">
              <div className="mb-4">
                <Button variant="outline" onClick={() => setIsDialogOpen(true)}>
                  Добавить начальника цеха
                </Button>
              </div>

              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent aria-describedby={undefined}>
                  <DialogTitle>Добавить начальника цеха</DialogTitle>
                  <Form {...foreman_form}>
                    <form onSubmit={foreman_form.handleSubmit(onForemanCreate)}>
                      <div className="space-y-2">
                        <FormField
                          control={foreman_form.control}
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
                          control={foreman_form.control}
                          name="gender"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Пол</FormLabel>
                              <FormControl>
                                <Input {...field} placeholder="М/Ж" required />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={foreman_form.control}
                          name="workshop"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Цех</FormLabel>
                              <FormControl>
                                <Input {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={foreman_form.control}
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
                        Добавить
                      </Button>
                    </form>
                  </Form>
                </DialogContent>
              </Dialog>

              <ForemenTable editable />
            </TabsContent>

            <TabsContent value="technicians">
              <div className="mb-4">
                <Button variant="outline" onClick={() => setIsDialogOpen(true)}>
                  Добавить технического работника
                </Button>
              </div>

              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent aria-describedby={undefined}>
                  <DialogTitle>Добавить технического работника</DialogTitle>
                  <Form {...technician_form}>
                    <form
                      onSubmit={technician_form.handleSubmit(
                        onTechnicianCreate,
                      )}
                    >
                      <div className="space-y-2">
                        <FormField
                          control={technician_form.control}
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
                          control={technician_form.control}
                          name="gender"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Пол</FormLabel>
                              <FormControl>
                                <Input {...field} placeholder="М/Ж" required />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={technician_form.control}
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
                          control={technician_form.control}
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
                        Добавить
                      </Button>
                    </form>
                  </Form>
                </DialogContent>
              </Dialog>
              <TechniciansTable />
            </TabsContent>
          </CardContent>
        </Tabs>
      </Card>
    </div>
  );
};

export default ForemenPage;
