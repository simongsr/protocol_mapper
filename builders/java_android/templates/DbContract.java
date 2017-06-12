package {{ package }};

import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.Context;
import android.net.Uri;
import android.provider.BaseColumns;
import android.util.log.Log;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Created by ProtocolMapper on {{ now }}.
 */
public class {{ contract_name }} {

    public static final String TAG = "{{ contract_name }}";

    public static final String CONTENT_AUTHORITY = "{{ package }}.provider";

    public static final Uri BASE_CONTENT_URI = Uri.parse("content://" + CONTENT_AUTHORITY);


    {% for model in schema|core.models(reverse=True) %}
    public static final String {{ model|java_android.path_name }} = "{{ model.fullname|join('__')|lower }}";
    {% endfor %}




    public static final String DATE_FORMAT = "yyyyMMdd";

    public static String formatDateToString(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_FORMAT);
        return sdf.format(date);
    }

    public static Date formatStringToDate(String dateText) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_FORMAT);
        try {
            return sdf.parse(dateText);
        } catch (ParseException ex) {
            Log.error(TAG, ex.getMessage());
        }
        return null;
    }



    {% for model in schema|core.models(reverse=True) %}

        {% if model|java_android.is_shared_pref_model %}


    public static class {{ model|java_android.entry_name }} {

        public static final String FILENAME = "{{ model.full_name|join('__') }}";  // TODO da testare
        public static final int MODE = Context.MODE_PRIVATE;

        {% for field in model|java_android.fields %}
        public static final String {{ field.name|java_android.field_name }} = "{{ field.name }}";
        {% endfor %}

    }


        {% else %}


    public static class {{ model|java_android.entry_name }} implements BaseColumns {

        public static final Uri CONTENT_URI = BASE_CONTENT_URI.buildUpon()
                                                              .appendPath({{ model|java_android.path_name }})
                                                              .build();

        public static final String CONTENT_DIR_TYPE = ContentResolver.CURSOR_DIR_BASE_TYPE +
                                                      "/" +
                                                      CONTENT_AUTHORITY +
                                                      "/" +
                                                      {{ model|java_android.path_name }};
        public static final String CONTENT_ITEM_TYPE = ContentResolver.CURSOR_ITEM_BASE_TYPE +
                                                       "/" +
                                                       CONTENT_AUTHORITY +
                                                       "/" +
                                                       {{ model|java_android.path_name }};

        public static final String TABLE_NAME = "{{ model|java_android.table_name }}";

        {% for field in model|java_android.fields %}
        public static final String {{ field|java_android.field_name }} = "{{ field|java_android.column_name }}";
        {% endfor %}

        public static final String[] COLUMNS = {
            _ID,
            {% for field in model|java_android.fields %}
            {{ field|java_android.field_name }},
            {% endfor %}
        };

        public static final int INDEX__ID = 0;
        {% for field in model|java_android.fields %}
        public static final int {{ field|java_android.index_name }} = {{ loop.index }};
        {% endfor %}


        public static Uri buildUriFromId(long id) {
            return ContentUris.withAppendedId(CONTENT_URI, id);
        }

        public static String getIdFromUri(Uri uri) {
            return uri.getLastPathSegment();
        }

    }


        {% endif %}

    {% endfor %}



}

