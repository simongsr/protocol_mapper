package {{ package }};

import android.annotation.TargetApi;
import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.UriMatcher;
import android.database.Cursor;
import android.database.SQLException;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteQueryBuilder;
import android.net.Uri;
import android.os.Build;

import java.util.Set;

{% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
import {{ package }}.{{ contract_name }}.{{ model.full_name|java_android.entry_name }};
{% endfor %}

{% for full_name in schema.models %}
import {{ package }}.models.{{ full_name|java.class_name }};
{% endfor %}

/**
 * Created by ProtocolMapper on {{ now }}.
 */
public class {{ provider_name }} extends ContentProvider {

    {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
    private static final int {{ model.full_name|upper|replace('.', '__') }}         = {{ loop.index * 100 }};
    private static final int {{ model.full_name|upper|replace('.', '__') }}_WITH_ID = {{ loop.index * 100 + 1 }};

    {% endfor %}




    private static final UriMatcher sUriMatcher = buildUriMatcher();

    private              {{ helper_name }} mOpenHelper;


    {% for model in schema|utils.visit_models if model|java_android.is_join_model %}
    private static final SQLiteQueryBuilder {{ model|java_android.join_model_query_builder_name }};
    {% endfor %}


    static {

        {% for model in schema|utils.visit_models if model|java_android.is_join_model and model.dest_field.ref_model != None %}
        {{ model|java_android.join_model_query_builder_name }} = new SQLiteQueryBuilder();
        {{ model|java_android.join_model_query_builder_name }}.setTables(
            {{ model.full_name|java_android.entry_name }}.TABLE_NAME +
            " INNER JOIN " +
            {{ model.source_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME +
            " INNER JOIN " +
            {{ model.dest_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME +
            " ON " +
            {{ model.full_name|java_android.entry_name }}.TABLE_NAME + "." +
                {{ model.full_name|java_android.entry_name }}.{{ model.source_field|java_android.column_name }} +
            " = " +
            {{ model.source_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME + "." +
                {{ model.source_field.ref_model.full_name|java_android.entry_name }}._ID +
            " AND " +
            {{ model.full_name|java_android.entry_name }}.TABLE_NAME + "." +
                {{ model.full_name|java_android.entry_name }}.{{ model.dest_field|java_android.column_name }} +
            " = " +
            {{ model.dest_field.ref_model.full_name|java_android.entry_name }}.TABLE_NAME + "." +
                {{ model.dest_field.ref_model.full_name|java_android.entry_name }}._ID
        );

        {% endfor %}
    }




    private static UriMatcher buildUriMatcher() {
        final UriMatcher matcher = new UriMatcher(UriMatcher.NO_MATCH);

        final String authority = {{ contract_name }}.CONTENT_AUTHORITY;


        {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
        matcher.addURI(authority, {{ contract_name }}.{{ model.full_name|java_android.path_name }}, {{ model.full_name|upper|replace('.', '__') }});
        matcher.addURI(authority, {{ contract_name }}.{{ model.full_name|java_android.path_name }} + "/#", {{ model.full_name|upper|replace('.', '__') }}_WITH_ID);

        {% endfor %}

        return matcher;
    }












    {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
    /*
     * {{ model.full_name|java_android.entry_name }}
     */
     private Cursor query{{ model.full_name|replace('.', '__') }}(Uri uri,
                                SQLiteDatabase db,
                                String[] projection,
                                String selection,
                                String[] selectionArgs,
                                String sortOrder) {

        {% if not model|java_android.is_join_model %}
        return db.query(
                {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                projection,
                selection,
                selectionArgs,
                null,
                null,
                sortOrder
        );
        {% else %}
        return {{ model|java_android.join_model_query_builder_name }}.query(
                db,
                projection,
                selection,
                selectionArgs,
                null,
                null,
                sortOrder
        );
        {% endif %}
    }

    private Uri insert{{ model.full_name|replace('.', '__') }}(Uri uri,
                              SQLiteDatabase db,
                              ContentValues values) {

        long id = db.insert(
                {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                null,
                values
        );
        if (id <= 0) {
            throw new SQLException("Failed to insert row into " + uri);
        }
        return {{ model.full_name|java_android.entry_name }}.buildUriFromId(id);
    }

    private int update{{ model.full_name|replace('.', '__') }}(Uri uri,
                              SQLiteDatabase db,
                              ContentValues values) {

        String id = {{ model.full_name|java_android.entry_name }}.getIdFromUri(uri);
        return db.update(
                {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                values,
                {{ model.full_name|java_android.entry_name }}._ID + " = ?",
                new String[] {
                        id
                }
        );
    }

    private int delete{{ model.full_name|replace('.', '__') }}(Uri uri,
                              SQLiteDatabase db) {

        String id = {{ model.full_name|java_android.entry_name }}.getIdFromUri(uri);
        return db.delete(
                {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                {{ model.full_name|java_android.entry_name }}._ID + " = ?",
                new String[] {
                        id
                }
        );
    }

    private int delete{{ model.full_name|replace('.', '__') }}(Uri uri,
                              SQLiteDatabase db,
                              String selection,
                              String[] selectionArgs) {

        return db.delete(
                {{ model.full_name|java_android.entry_name }}.TABLE_NAME,
                selection,
                selectionArgs
        );
    }
    // {{ model.full_name|java_android.entry_name }}

    {% endfor %}












    @Override
    public boolean onCreate() {
        mOpenHelper = new {{ helper_name }}(getContext());
        return true;
    }

    @Override
    public String getType(Uri uri) {
        final int match = sUriMatcher.match(uri);
        switch (match) {

            {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
            case {{ model.full_name|upper|replace('.', '__') }}:
                return {{ model.full_name|java_android.entry_name }}.CONTENT_DIR_TYPE;
            case {{ model.full_name|upper|replace('.', '__') }}_WITH_ID:
                return {{ model.full_name|java_android.entry_name }}.CONTENT_ITEM_TYPE;


            {% endfor %}


            default:
                throw new UnsupportedOperationException("Unknown uri: " + uri);
        }
    }

    @Override
    public Cursor query(Uri uri,
                        String[] projection,
                        String selection,
                        String[] selectionArgs,
                        String sortOrder) {

        Cursor retCursor = null;
        final SQLiteDatabase db = mOpenHelper.getReadableDatabase();

        final int match = sUriMatcher.match(uri);
        switch (match) {

            {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
            case {{ model.full_name|upper|replace('.', '__') }}:
                retCursor = query{{ model.full_name|replace('.', '__') }}(
                        uri,
                        db,
                        projection,
                        selection,
                        selectionArgs,
                        sortOrder
                );
                break;

            case {{ model.full_name|upper|replace('.', '__') }}_WITH_ID:
                retCursor = query{{ model.full_name|replace('.', '__') }}(
                        uri,
                        db,
                        projection,
                        selection,
                        selectionArgs,
                        sortOrder
                );
                break;


            {% endfor %}

            default:
                throw new UnsupportedOperationException("Unknown uri: " + uri);
        }

        retCursor.setNotificationUri(getContext().getContentResolver(), uri);

        return retCursor;
    }

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
    @Override
    public Uri insert(Uri uri, ContentValues values) {
        final SQLiteDatabase db = mOpenHelper.getWritableDatabase();
        db.setForeignKeyConstraintsEnabled(true);

        Uri returnUri = null;

        final int match = sUriMatcher.match(uri);
        switch (match) {

            {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
            case {{ model.full_name|upper|replace('.', '__') }}:
                returnUri = insert{{ model.full_name|replace('.', '__') }}(uri, db, values);
                break;

            {% endfor %}

            default:
                throw new UnsupportedOperationException("Unknown uri: " + uri);
        }

        getContext().getContentResolver().notifyChange(uri, null);

        return returnUri;
    }

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        final SQLiteDatabase db = mOpenHelper.getWritableDatabase();
        db.setForeignKeyConstraintsEnabled(true);

        int rowsUpdated = 0;

        final int match = sUriMatcher.match(uri);
        switch (match) {

            {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
            case {{ model.full_name|upper|replace('.', '__') }}_WITH_ID:
                rowsUpdated = update{{ model.full_name|replace('.', '__') }}(uri, db, values);
                break;

            {% endfor %}

            default:
                throw new UnsupportedOperationException("Unknown uri: " + uri);
        }

        if (rowsUpdated > 0) {
            getContext().getContentResolver().notifyChange(uri, null);
        }

        return rowsUpdated;
    }

    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) {
        final SQLiteDatabase db = mOpenHelper.getWritableDatabase();
        db.setForeignKeyConstraintsEnabled(true);

        int rowsDeleted = 0;

        final int match = sUriMatcher.match(uri);
        switch (match) {

            {% for model in schema|utils.visit_models if not model|java_android.is_shared_pref_model %}
            case {{ model.full_name|upper|replace('.', '__') }}:
                rowsDeleted = delete{{ model.full_name|replace('.', '__') }}(
                        uri,
                        db,
                        selection,
                        selectionArgs
                );
                break;

            case {{ model.full_name|upper|replace('.', '__') }}_WITH_ID:
                rowsDeleted = delete{{ model.full_name|replace('.', '__') }}(
                        uri,
                        db
                );
                break;


            {% endfor %}

            default:
                throw new UnsupportedOperationException("Unknown uri: " + uri);
        }

        if (selection == null || rowsDeleted > 0) {
            getContext().getContentResolver().notifyChange(uri, null);
        }

        return rowsDeleted;
    }

}

