import { Button } from "@/shared/ui/default/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/shared/ui/default/card";
import { Dialog, DialogContent, DialogTitle } from "@/shared/ui/default/dialog";
import { Input } from "@/shared/ui/default/input";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/ui/default/form";
import { apiInstance } from "@/shared/api/api-instance";
import { toast } from "sonner";

const FormSchema = z.object({
  id: z.coerce
    .number({ message: "Идентификатор должен быть натуральным числом" })
    .min(1, "Идентификатор должен быть натуральным числом")
    .int("Идентификатор должен быть натуральным числом"),
});

export const fetchTechnician = async (technicianId: number) => {
  try {
    const { data } = await apiInstance.get(`/technicians/${technicianId}`);
    return data;
  } catch (error) {
    throw new Error("Technician not found");
  }
};

const UserSelectionPage = () => {
  const navigate = useNavigate();

  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  const onSubmit = async (data: z.infer<typeof FormSchema>) => {
    try {
      const technician = await fetchTechnician(data.id);
      navigate(`/technicians/${technician.technician_id}`);
    } catch (error) {
      toast.error(`Технический работник ${data.id} не найден`);
    }
  };
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-96 shadow-md">
        <CardHeader>
          <CardTitle className="text-center">Выбор пользователя</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <Button
            className="w-full"
            variant="outline"
            onClick={() => setIsDialogOpen(true)}
          >
            Технический работник
          </Button>
          <Button
            className="w-full"
            variant="outline"
            onClick={() => navigate("/foremen")}
          >
            Начальник цеха
          </Button>
        </CardContent>
      </Card>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent aria-describedby={undefined}>
          <DialogTitle>Введите табельный номер работника</DialogTitle>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <FormField
                control={form.control}
                name="id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Табельный номер</FormLabel>
                    <FormControl>
                      <Input
                        required
                        {...field}
                        value={undefined}
                        autoComplete="off"
                        autoCorrect="off"
                        spellCheck="false"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="mt-4">
                Перейти
              </Button>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserSelectionPage;
