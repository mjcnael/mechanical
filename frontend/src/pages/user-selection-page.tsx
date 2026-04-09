import { Button } from "@/shared/ui/default/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/shared/ui/default/card";
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
import { apiInstance, getApiErrorMessage } from "@/shared/api/api-instance";
import { setCurrentUser, setToken } from "@/shared/auth";
import { normalizePhoneNumber } from "@/shared/phone";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/shared/ui/default/tabs";
import { toast } from "sonner";

const FormSchema = z.object({
  phone_number: z.preprocess(
    (value) => (typeof value === "string" ? normalizePhoneNumber(value) : value),
    z.string().regex(/^\+7\d{10}$/, "Неверный формат номера телефона"),
  ),
  password: z.string().min(1, "Заполните все обязательные поля"),
});

type LoginForm = z.infer<typeof FormSchema>;
type LoginRole = "foreman" | "technician";

type LoginResponse = {
  access_token: string;
  role: LoginRole;
  user_id: number;
  full_name: string;
};

const login = async (role: LoginRole, form: LoginForm) => {
  const { data } = await apiInstance.post<LoginResponse>("/auth/login", {
    role,
    ...form,
  });
  return data;
};

const UserSelectionPage = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<LoginRole>("foreman");

  const form = useForm<LoginForm>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      phone_number: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      const normalizedData = {
        ...data,
        phone_number: normalizePhoneNumber(data.phone_number),
      };
      const user = await login(role, normalizedData);
      setToken(user.access_token);
      setCurrentUser({
        role: user.role,
        user_id: user.user_id,
        full_name: user.full_name,
        phone_number: normalizedData.phone_number,
      });

      navigate(user.role === "technician" ? `/technicians/${user.user_id}` : "/foremen");
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-96 shadow-md">
        <CardHeader>
          <CardTitle className="text-center">Вход</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs
            value={role}
            onValueChange={(value) => setRole(value as LoginRole)}
            className="w-full"
          >
            <TabsList className="w-full">
              <TabsTrigger value="foreman" className="w-full">
                Начальник
              </TabsTrigger>
              <TabsTrigger value="technician" className="w-full">
                Техник
              </TabsTrigger>
            </TabsList>
            <TabsContent value="foreman" />
            <TabsContent value="technician" />
          </Tabs>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="phone_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Номер телефона</FormLabel>
                    <FormControl>
                      <Input
                        required
                        {...field}
                        autoComplete="tel"
                        autoCorrect="off"
                        spellCheck="false"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Пароль</FormLabel>
                    <FormControl>
                      <Input required type="password" autoComplete="current-password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full">
                Войти
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserSelectionPage;
