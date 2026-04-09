import { apiInstance, getApiErrorMessage } from "@/shared/api/api-instance";
import { Button } from "@/shared/ui/default/button";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { toast } from "sonner";

type NotificationDto = {
  notification_id: number;
  task_id: number | null;
  message: string;
  is_read: boolean;
  created_at: string;
};

const fetchNotifications = async () => {
  const { data } = await apiInstance.get<NotificationDto[]>("/notifications");
  return data;
};

export const fetchUnreadCount = async () => {
  const { data } = await apiInstance.get<{ unread_count: number }>(
    "/notifications/unread-count",
  );
  return data;
};

const markAsRead = async (notificationId: number) => {
  return await apiInstance.post(`/notifications/${notificationId}/read`);
};

const NotificationsList = () => {
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery(
    "notifications",
    fetchNotifications,
    {
      refetchInterval: 10000,
    },
  );

  const readMutation = useMutation(
    (notificationId: number) => markAsRead(notificationId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["notifications"]);
        queryClient.invalidateQueries(["notifications-unread-count"]);
      },
      onError: (error) => {
        toast.error(getApiErrorMessage(error));
      },
    },
  );

  if (isLoading) {
    return <div>Загрузка...</div>;
  }

  if (data.length === 0) {
    return <div>Уведомлений пока нет</div>;
  }

  return (
    <div className="space-y-3">
      {data.map((notification) => (
        <div
          key={notification.notification_id}
          className="rounded-md border p-3 flex items-start justify-between gap-3"
        >
          <div>
            <p className={notification.is_read ? "text-muted-foreground" : ""}>
              {notification.message}
            </p>
            <p className="text-sm text-muted-foreground">
              {new Date(notification.created_at).toLocaleString()}
            </p>
          </div>
          {!notification.is_read && (
            <Button
              variant="outline"
              onClick={() => readMutation.mutate(notification.notification_id)}
            >
              Отметить как прочитано
            </Button>
          )}
        </div>
      ))}
    </div>
  );
};

export default NotificationsList;
