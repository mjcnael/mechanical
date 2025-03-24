import ForemenTable from "@/features/foremen-table";
import TasksTable from "@/features/tasks-table";
import { apiInstance } from "@/shared/api/api-instance";
import { Card, CardContent, CardHeader } from "@/shared/ui/default/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/shared/ui/default/tabs";
import { useQuery } from "react-query";
import { useParams } from "react-router-dom";

export const fetchTechnician = async (technicianId: string) => {
  const { data } = await apiInstance.get(`/technicians/${technicianId}`);
  return data;
};

const TechniciansPage = () => {
  const { id } = useParams();

  if (!id) return <>Пусто...</>;

  const { data: technician, isLoading } = useQuery([`technician-${id}`], () =>
    fetchTechnician(id),
  );

  if (isLoading) {
    return <div>Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <Card className="w-full">
        <Tabs defaultValue="tasks" className="w-full">
          <CardHeader className="flex-row items-center justify-between pb-2">
            <h1 className="text-xl font-bold">Технический работник</h1>
            <TabsList>
              <TabsTrigger value="tasks">Задачи</TabsTrigger>
              <TabsTrigger value="foremen">Начальники цехов</TabsTrigger>
              <TabsTrigger value="profile">Профиль</TabsTrigger>
            </TabsList>
          </CardHeader>
          <CardContent>
            <TabsContent value="tasks">
              <TasksTable />
            </TabsContent>
            <TabsContent value="foremen">
              <ForemenTable />
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
