package com.crusty.lessons;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;

public class Schedule {

    public static class Lesson {
        public final int number, start, end;
        Lesson(int number, int start, int end) {
            this.number = number;
            this.start = start;
            this.end = end;
        }
    }

    public static class Status {
        public String timer;
        public String next;
        public int progress;
        public boolean activeDay;
        public List<Lesson> lessons;
        public int currentIndex = -1;
    }

    public static List<Lesson> build(Profile p) {
        List<Lesson> out = new ArrayList<>();
        int t = p.startMin;
        for (int i = 0; i < p.lessonCount; i++) {
            out.add(new Lesson(i + 1, t, t + p.lessonMin));
            t += p.lessonMin;
            if (i < p.breaks.length) t += p.breaks[i];
        }
        return out;
    }

    public static boolean isSchoolDay(Profile p, Calendar cal) {
        int dow = cal.get(Calendar.DAY_OF_WEEK); // 1 = Вс ... 7 = Сб
        int bit = (dow + 5) % 7;                  // 0 = Пн ... 6 = Вс
        return (p.days & (1 << bit)) != 0;
    }

    public static Status status(Profile p, Calendar cal) {
        Status s = new Status();
        s.lessons = build(p);
        s.activeDay = isSchoolDay(p, cal);

        if (!s.activeDay) {
            s.timer = "Сегодня выходной";
            s.next = "Учебные дни: " + daysText(p.days);
            s.progress = 0;
            return s;
        }

        int now = cal.get(Calendar.HOUR_OF_DAY) * 60 + cal.get(Calendar.MINUTE);

        for (int i = 0; i < s.lessons.size(); i++) {
            Lesson l = s.lessons.get(i);
            if (now >= l.start && now < l.end) {
                s.currentIndex = i;
                int left = l.end - now;
                boolean last = i + 1 >= s.lessons.size();
                s.timer = (last ? "До конца смены: " : "До перемены: ") + left + " мин";
                s.progress = (now - l.start) * 100 / (l.end - l.start);
                if (last) {
                    s.next = "Последний урок";
                } else {
                    Lesson n = s.lessons.get(i + 1);
                    s.next = "Далее: Урок " + n.number + " в " + fmt(n.start);
                }
                return s;
            }
        }

        for (Lesson l : s.lessons) {
            if (now < l.start) {
                s.timer = "До урока: " + (l.start - now) + " мин";
                s.next = "Далее: Урок " + l.number + " в " + fmt(l.start);
                s.progress = 0;
                return s;
            }
        }

        s.timer = "Уроки закончились";
        s.next = "На сегодня всё";
        s.progress = 100;
        return s;
    }

    public static String fmt(int minutes) {
        return String.format(Locale.US, "%02d:%02d", minutes / 60, minutes % 60);
    }

    public static String daysText(int mask) {
        String[] names = {"Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"};
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 7; i++) {
            if ((mask & (1 << i)) != 0) {
                if (sb.length() > 0) sb.append(" ");
                sb.append(names[i]);
            }
        }
        return sb.length() == 0 ? "не выбраны" : sb.toString();
    }
}
