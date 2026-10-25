package com.crusty.lessons;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import java.util.Calendar;

public class LessonService extends Service {

    private static final String CHANNEL = "crusty_status";
    private static final int NOTIF_ID = 1;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable tick = new Runnable() {
        @Override
        public void run() {
            refresh();
            handler.postDelayed(this, 30000L);
        }
    };

    @Override
    public void onCreate() {
        super.onCreate();
        NotificationChannel ch = new NotificationChannel(
                CHANNEL, "Текущий урок", NotificationManager.IMPORTANCE_LOW);
        getSystemService(NotificationManager.class).createNotificationChannel(ch);

        Notification n = buildNotification();
        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else {
            startForeground(NOTIF_ID, n);
        }
        handler.post(tick);
    }

    private void refresh() {
        getSystemService(NotificationManager.class).notify(NOTIF_ID, buildNotification());
        WidgetUpdater.updateAll(this);
    }

    private Notification buildNotification() {
        Profile p = new Store(this).getActive();
        Schedule.Status st = Schedule.status(p, Calendar.getInstance());
        PendingIntent pi = PendingIntent.getActivity(this, 0,
                new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, CHANNEL)
                .setSmallIcon(android.R.drawable.ic_menu_recent_history)
                .setColor(0xFF1B5E20)
                .setContentTitle(p.name + " · " + st.timer)
                .setContentText(st.next)
                .setStyle(new Notification.BigTextStyle().bigText(st.next + "\n@CrustySearch"))
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setSilent(true)
                .setContentIntent(pi)
                .build();
    }

    @Override
    public void onDestroy() {
        handler.removeCallbacks(tick);
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
