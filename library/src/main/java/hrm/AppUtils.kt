package hrm

import android.app.Activity
import android.app.PendingIntent
import android.content.Context
import android.content.ContextWrapper
import android.content.SharedPreferences
import android.content.res.Configuration
import android.os.Build
import android.view.View
import androidx.annotation.DrawableRes
import androidx.appcompat.app.AppCompatDelegate
import java.util.Locale


object AppUtils {

    private lateinit var appActivity: Activity

    fun initialize(activity: Activity) {
        appActivity = activity
        NetworkUtils.initialize(activity)
    }

    fun getActivity(): Activity {
        if (!::appActivity.isInitialized)
            throw IllegalStateException("Call AppUtils.initialize(activity) first")
        return appActivity
    }
// ---------------- Locale / Language ----------------
private const val PREF = "locale_prefs"
private const val KEY_LANG = "lang"

private fun prefs(context: Context): SharedPreferences =
    context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

fun saveLanguage(context: Context, lang: String) {
    val normalized = lang.trim()
    if (normalized.isEmpty()) return

    prefs(context).edit().putString(KEY_LANG, normalized).apply()

    // API 33+ -> use AppCompatDelegate application locales
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        val localeList = androidx.core.os.LocaleListCompat.forLanguageTags(normalized)
        AppCompatDelegate.setApplicationLocales(localeList)
    }
}

fun loadLanguage(context: Context): String? =
    prefs(context).getString(KEY_LANG, null)

/** simple helper (minSdk >= 21 so forLanguageTag is safe) */
private fun createLocale(tagOrLang: String): Locale {
    return Locale.forLanguageTag(tagOrLang.trim())
}

fun attachBaseContext(base: Context): ContextWrapper {
    val lang = loadLanguage(base) ?: return ContextWrapper(base)

    // API 33+: AppCompatDelegate will handle application locales
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        val localeList = androidx.core.os.LocaleListCompat.forLanguageTags(lang)
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

fun setLanguage(lang: String) {
    val ctx = getActivity() ?: return
    val normalized = lang.trim()
    if (normalized.isEmpty()) return

    saveLanguage(ctx, normalized)

    // API 33+ -> AppCompatDelegate
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        val localeList = androidx.core.os.LocaleListCompat.forLanguageTags(normalized)
        AppCompatDelegate.setApplicationLocales(localeList)
        return
    }

    // API 23..32 -> apply configuration to current Activity if available
    val locale = createLocale(normalized)
    Locale.setDefault(locale)
    val newConfig = Configuration(ctx.resources.configuration)
    newConfig.setLocale(locale)

    // applyOverrideConfiguration works on Activity; use it when possible
    val activity = ctx as? android.app.Activity
    if (activity != null) {
        activity.applyOverrideConfiguration(newConfig)
    } else {
        // fallback: create a configuration context (does not modify global resources)
        ctx.createConfigurationContext(newConfig)
    }
}

    // ---------------- Network ----------------
    val isConnected: Boolean
        get() = NetworkUtils.isConnected

    fun addConnectionListener(listener: (Boolean) -> Unit) =
        NetworkUtils.addConnectionListener(listener)

    // ---------------- Snackbar ----------------
    fun showSnackbar(
        parentView: View,
        message: String,
        iconRes: Int? = null,
        actionText: String? = null,
        actionListener: View.OnClickListener? = null,
        length: Int = SnackbarUtils.LENGTH_SHORT,
        position: SnackbarUtils.SnackbarPosition = SnackbarUtils.SnackbarPosition.BOTTOM
    ) {
        SnackbarUtils.showSnackbar(
            parentView = parentView,
            message = message,
            iconRes = iconRes ?: 0,
            actionText = actionText ?: "",
            actionListener = actionListener ?: View.OnClickListener { },
            length = length,
            position = position
        )
    }

    // ---------------- Vibration ----------------
    fun vibrate(milliseconds: Long) =
        VibrationUtils.vibrate(getActivity(), milliseconds)

    fun vibratePattern(pattern: LongArray, repeat: Int) =
        VibrationUtils.vibratePattern(getActivity(), pattern, repeat)

    // ---------------- Screen Capture ----------------
    fun blockCapture() = ScreenUtils.blockCapture(getActivity())
    fun unblockCapture() = ScreenUtils.unblockCapture(getActivity())

    // ---------------- Notification ----------------
    fun showNotification(
        channelId: String,
        title: String,
        text: String,
        @DrawableRes iconResId: Int,
        intent: PendingIntent? = null
    ) = NotificationUtils.showNotification(getActivity(), channelId, title, text, iconResId, intent)

    // ---------------- Browser ----------------
    fun openUrl(url: String) = BrowserUtils.openUrl(getActivity(), url)

    // ---------------- Signature ----------------
    fun getAppSignatures(): List<String> =
        SignatureUtils.getAppSignatures(getActivity())

    fun validateAppSignature(sha1: String): Boolean =
        SignatureUtils.validateAppSignature(getActivity(), sha1)

    // ---------------- Dialog ----------------
    fun showDialog(
        title: String,
        message: String,
        positiveButton: String = "OK",
        onPositiveClick: (() -> Unit)? = null
    ) = DialogUtils.showDialog(getActivity(), title, message, positiveButton, onPositiveClick)

    // ---------------- Clipboard ----------------
    fun copyText(text: String) = ClipboardUtils.copyText(getActivity(), text)
    fun getCopiedText(): String? = ClipboardUtils.getText(getActivity())

    // ---------------- Toast ----------------
    fun showToast(message: String, long: Boolean = false) {
        if (long) ToastUtils.showLong(getActivity(), message)
        else ToastUtils.showShort(getActivity(), message)
    }

    // ---------------- File ----------------
    fun writeFile(name: String, content: String) =
        FileUtils.writeFile(getActivity(), name, content)

    fun readFile(name: String): String? =
        FileUtils.readFile(getActivity(), name)

    fun deleteFile(name: String): Boolean =
        FileUtils.deleteFile(getActivity(), name)

    // ---------------- Keyboard ----------------
    fun hideKeyboard() = KeyboardUtils.hideKeyboard(getActivity())
}