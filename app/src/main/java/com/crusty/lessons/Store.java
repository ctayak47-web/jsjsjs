package com.crusty.lessons;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class Store {
    private static final String PREFS = "crusty_lessons";
    private final SharedPreferences prefs;

    public Store(Context c) {
        prefs = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public List<Profile> getProfiles() {
        List<Profile> list = new ArrayList<>();
        try {
            JSONArray arr = new JSONArray(prefs.getString("profiles", "[]"));
            for (int i = 0; i < arr.length(); i++) {
                JSONObject o = arr.getJSONObject(i);
                list.add(Profile.fromJson(o));
            }
        } catch (Exception ignored) { }
        if (list.isEmpty()) {
            Profile p = new Profile();
            list.add(p);
            saveProfiles(list);
            setActiveId(p.id);
        }
        return list;
    }

    public void saveProfiles(List<Profile> list) {
        try {
            JSONArray arr = new JSONArray();
            for (Profile p : list) arr.put(p.toJson());
            prefs.edit().putString("profiles", arr.toString()).apply();
        } catch (Exception ignored) { }
    }

    public Profile getActive() {
        List<Profile> list = getProfiles();
        String id = prefs.getString("active", "");
        for (Profile p : list) if (p.id.equals(id)) return p;
        setActiveId(list.get(0).id);
        return list.get(0);
    }

    public void setActiveId(String id) {
        prefs.edit().putString("active", id).apply();
    }

    public String getTheme() {
        return prefs.getString("theme", "green");
    }

    public void setTheme(String theme) {
        prefs.edit().putString("theme", theme).apply();
    }
}
