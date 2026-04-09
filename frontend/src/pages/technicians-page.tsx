import NotificationsList, {
  fetchUnreadCount,
} from "@/features/notifications-list";
import TasksTable from "@/features/tasks-table";
import { apiInstance } from "@/shared/api/api-instance";
import { getCurrentUser, logout } from "@/shared/auth";
import { Button } from "@/shared/ui/default/button";
import { Card, CardContent, CardHeader } from "@/shared/ui/default/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/shared/ui/default/tabs";
import { useEffect } from "react";
import { useQuery } from "react-query";
import { useNavigate, useParams } from "react-router-dom";

export const fetchTechnician = async (technicianId: string) => {
  const { data } = await apiInstance.get(`/technicians/${technicianId}`);
  return data;
};

const TechniciansPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const currentUser = getCurrentUser();
  const canOpenPage =
    !!id &&
    currentUser?.role === "technician" &&
    currentUser.user_id === Number(id);

  useEffect(() => {
    if (!canOpenPage) {
      navigate("/", { replace: true });
    }
  }, [canOpenPage, navigate]);

  const { data: technician, isLoading } = useQuery(
    [`technician-${id}`],
    () => fetchTechnician(id!),
    { enabled: canOpenPage },
  );
  const { data: unreadNotifications } = useQuery(
    "notifications-unread-count",
    fetchUnreadCount,
    {
      enabled: canOpenPage,
      refetchInterval: 10000,
    },
  );

  if (!canOpenPage) return <>Доступ запрещён</>;

  if (isLoading) {
    return <div>Загрузка...</div>;
  }

  const onLogout = () => {
    logout();
    navigate("/", { replace: true });
  };

  return (
    <div className="p-6">
      <Card className="w-full">
        <Tabs defaultValue="tasks" className="w-full">
          <CardHeader className="flex-row items-center justify-between pb-2">
            <h1 className="text-xl font-bold">Технический работник</h1>
            <div className="flex items-center gap-2">
              <TabsList>
                <TabsTrigger value="tasks">Задачи</TabsTrigger>
                <TabsTrigger value="notifications" className="relative">
                  Уведомления
                  {!!unreadNotifications?.unread_count && (
                    <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
                  )}
                </TabsTrigger>
                <TabsTrigger value="profile">Профиль</TabsTrigger>
              </TabsList>
              <Button variant="outline" onClick={onLogout}>
                Выйти
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <TabsContent value="tasks">
              <TasksTable />
            </TabsContent>
            <TabsContent value="notifications">
              <NotificationsList />
            </TabsContent>
            <TabsContent value="profile">
              <div className="space-y-2">
                <p>Табельный номер: {technician.technician_id}</p>
                <p>ФИО: {technician.full_name}</p>
                <p>Пол: {technician.gender}</p>
                <p>Специализация: {technician.specialization}</p>
                <p>Телефон: {technician.phone_number}</p>
              </div>
            </TabsContent>
          </CardContent>
        </Tabs>
      </Card>
    </div>
  );
};

export default TechniciansPage;
