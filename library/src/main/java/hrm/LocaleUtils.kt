package hrm

import android.content.Context
import android.content.ContextWrapper
import android.content.SharedPreferences
import android.content.res.Configuration
import android.os.Build
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import java.util.Locale

/**
 * Locale utility functions.
 * Internal singleton so it can be used across the app but not exposed publicly.
 */
internal object LocaleUtils {

    private const val PREF = "locale_prefs"
    private const val KEY_LANG = "lang"

    private fun prefs(context: Context): SharedPreferences =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    private fun saveLanguage(context: Context, lang: String) {
        val normalized = lang.trim()
        if (normalized.isEmpty()) return

        prefs(context)
            .edit()
            .putString(KEY_LANG, normalized)
            .apply()

        // API 33+ -> use AppCompatDelegate application locales
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val localeList = LocaleListCompat.forLanguageTags(normalized)
            AppCompatDelegate.setApplicationLocales(localeList)
        }
    }

    fun loadLanguage(context: Context): String? =
        prefs(context).getString(KEY_LANG, null)

    /**
     * Create locale safely across all API levels.
     */
    private fun createLocale(tagOrLang: String): Locale {
        val trimmed = tagOrLang.trim()

        return when {
            // API 35+ : use Locale.of(...)
            Build.VERSION.SDK_INT >= 35 -> {
                val parts = trimmed.split("-", "_")
                when (parts.size) {
                    1 -> Locale.of(parts[0])
                    2 -> Locale.of(parts[0], parts[1])
                    3 -> Locale.of(parts[0], parts[1], parts[2])
                    else -> Locale.forLanguageTag(trimmed) // fallback
                }
            }

            else -> {
                // API 23..34 : safe with forLanguageTag
                Locale.forLanguageTag(trimmed)
            }
        }
    }

    /**
     * Attach saved locale to a base Context (call from Application.attachBaseContext).
     */
    fun attachBaseContext(base: Context): ContextWrapper {
        val lang = loadLanguage(base) ?: return ContextWrapper(base)

        // API 33+: AppCompatDelegate will handle application locales
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val localeList = LocaleListCompat.forLanguageTags(lang)
            AppCompatDelegate.setApplicationLocales(localeList)
            return ContextWrapper(base)
        }

        // For API 23..32: create a new configuration context with the chosen locale
        val locale = createLocale(lang)

        Locale.setDefault(locale)

        val config = Configuration(base.resources.configuration)
        config.setLocale(locale)

        val ctx = base.createConfigurationContext(config)

        return ContextWrapper(ctx)
    }

    /**
     * Apply language immediately. Accepts a Context (Activity preferred).
     */
    fun setLanguage(context: Context, lang: String) {
        val normalized = lang.trim()
        if (normalized.isEmpty()) return

        saveLanguage(context, normalized)

        // API 33+ -> AppCompatDelegate
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val localeList = LocaleListCompat.forLanguageTags(normalized)
            AppCompatDelegate.setApplicationLocales(localeList)
            return
        }

        // API 23..32 -> apply configuration to current Activity if available
        val locale = createLocale(normalized)

        Locale.setDefault(locale)

        val newConfig = Configuration(context.resources.configuration)
        newConfig.setLocale(locale)

        val activity = context as? android.app.Activity
        if (activity != null) {
            activity.applyOverrideConfiguration(newConfig)
        } else {
            // fallback: create a configuration context (does not modify global resources)
            context.createConfigurationContext(newConfig)
        }
    }
}
