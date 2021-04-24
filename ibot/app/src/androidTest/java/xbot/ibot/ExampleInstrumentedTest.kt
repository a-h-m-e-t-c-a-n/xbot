package xbot.ibot


import android.content.Context
import android.content.Intent
import android.media.MediaScannerConnection
import android.net.Uri
import android.util.Log
import androidx.test.core.app.ApplicationProvider.getApplicationContext
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File


/**
 * Instrumented test, which will execute on an Android device.
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */

//./gradlew connectedAndroidTest -i -Pandroid.testInstrumentationRunnerArguments.account=girlinthefire0 -Pandroid.testInstrumentationRunnerArguments.password=uyelik -Pandroid.testInstrumentationRunnerArguments.content="oldu"

@RunWith(AndroidJUnit4::class)
class IBotPublishInstagram {
    var account= ""
    var password= ""
    var content:String?= null
    fun launchInstagram() {
        val context: Context = getApplicationContext()

        val appIs = "http://instagram.com/"+account
        val urlIs = "http://instagram.com/_u/"+account
        try {
            val intent = Intent(Intent.ACTION_VIEW)
            intent.data = Uri.parse(appIs)
            intent.setPackage("com.instagram.android")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // Clear out any previous instances
            context.startActivity(intent)
        } catch (ex: Exception) {
            var view=Intent(
                Intent.ACTION_VIEW,
                Uri.parse(urlIs)
            )
            view.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // Clear out any previous instances

            context.startActivity(view)
        }
    }
    fun scanFiles(context:Context){
        val directory: File = File("/storage/emulated/0/Pictures")
        Log.w("ahmetcan",directory.absolutePath+" scanning")
        val listfiles = directory.listFiles()
        var files=listfiles.toList().sortedByDescending { it.name }
        Log.d("Files", "Size: " + files.size)
        for (i in files.indices) {
            Log.d("Files", "FileName:" + files[i].name)
            //MediaScannerConnection.scanFile(context, arrayOf<String>(File("/storage/emulated/0/Pictures").absolutePath), null, null);
            MediaScannerConnection.scanFile(context, arrayOf<String>(files[i].absolutePath), null, null);

        }
        MediaScannerConnection.scanFile(context, arrayOf<String>(directory.absolutePath), null, null);
    }

    @Test
    fun shareFeedPhoto() {
        var instagramns="com.instagram.android"


        // Context of the app under test.
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext

        scanFiles(appContext)

        //./gradlew connectedAndroidTest -i -Pandroid.testInstrumentationRunnerArguments.account=girlinthefire0 -Pandroid.testInstrumentationRunnerArguments.password=uyelik -Pandroid.testInstrumentationRunnerArguments.content="oldu"
        account= InstrumentationRegistry.getArguments().getString("account")?:"jessybiotic"
        password= InstrumentationRegistry.getArguments().getString("password")?:"gizli80."
        content= InstrumentationRegistry.getArguments().getString("content")

        Log.w("ac_upload", account + " " + password)
        Log.w("ac_upload", "bu bir testtir-------------------------------------------")

        var device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())

        launchInstagram()



        device.wait(Until.hasObject(By.pkg(instagramns).depth(0)), 10000)
        Thread.sleep(5000)

        device.wait(
            Until.hasObject(By.res("com.instagram.android:id/log_in_button")),
            10000
        )

        var request_loginentry=device.hasObject(By.res("com.instagram.android:id/login_username"))
        var request_login=device.hasObject(By.res("com.instagram.android:id/log_in_button"))

        if(request_login&&!request_loginentry){
            device.findObject(By.res("com.instagram.android:id/log_in_button")).click()
            Thread.sleep(5000)
        }
        //com.instagram.android:id/next_button
        //com.instagram.android:id/login_forgot_button
        //com.instagram.android:id/log_in_button
        if(device.hasObject(By.res("com.instagram.android:id/remove_text_link"))){
            device.findObject(By.res("com.instagram.android:id/remove_text_link")).click()
            Thread.sleep(5000)
            device.findObject(By.res("com.instagram.android:id/primary_button")).click()
            Thread.sleep(5000)
        }

        if(device.hasObject(By.res("com.instagram.android:id/login_username"))){
            device.findObject(By.res("com.instagram.android:id/login_username")).text=account
            device.findObject(By.res("com.instagram.android:id/password")).text=password
            device.findObject(By.res("com.instagram.android:id/next_button")).click()
            Thread.sleep(5000)

            launchInstagram()
        }


        //com.instagram.android:id/action_bar
        //device.findObject(By.res("com.instagram.android:id/action_bar")).children[1].resourceName
        device.wait(
            Until.hasObject(By.res("com.instagram.android:id/action_bar")),
            60000
        )
        Thread.sleep(5000)
        device.findObject(By.res("com.instagram.android:id/action_bar")).children[1].click()

        //com.instagram.android:id/label
        device.wait(
            Until.hasObject(By.textContains("Feed Post")),
            30000
        )
        device.findObject(By.textContains("Feed Post")).click()
        Thread.sleep(5000)
        try {
            device.findObject(By.textContains("GALLERY")).let {
                it.click()
                Thread.sleep(5000)
            }
        }
        catch (ex:java.lang.Exception){
            Log.e("ahmetcan","erro blocked GALLERY")
        }
        try {
            if(device.hasObject(By.res("com.android.permissioncontroller:id/permission_allow_button"))) {
                device.findObject(By.res("com.android.permissioncontroller:id/permission_allow_button")).let {
                    it.click()
                    Thread.sleep(5000)
                }
            }
        }
        catch (ex:java.lang.Exception){
            Log.e("ahmetcan","error blocked permission_allow_button")
        }


        try {
            if(device.hasObject(By.res("com.instagram.android:id/croptype_toggle_button"))){
                device.findObject(By.res("com.instagram.android:id/croptype_toggle_button")).let {
                    it.click()
                    Thread.sleep(5000)
                }
            }

        }
        catch (ex:java.lang.Exception){
            Log.e("ahmetcan","croptype_toggle_button bulunamadı")
        }
        

        try {


            device.findObject(By.res("com.instagram.android:id/multi_select_slide_button")).let {
                device.findObject(By.res("com.instagram.android:id/multi_select_slide_button")).click()
                Thread.sleep(5000)
            }


        }
        catch (ex:java.lang.Exception){
            Log.e("ahmetcan","multi_select_slide_button bulunamadı")

        }


        for(obj in device.findObject(By.res("com.instagram.android:id/media_picker_grid_view")).children.drop(1)){
            if(obj.isClickable){
                obj.click()
                Thread.sleep(1000)
            }

        }

        try {

            device.wait(Until.hasObject(By.res("com.instagram.android:id/next_button_imageview")), 10000)
            device.findObject(By.res("com.instagram.android:id/next_button_imageview")).click()
            Thread.sleep(20000)
        }
        catch (ex:java.lang.Exception){
            device.wait(Until.hasObject(By.res("com.instagram.android:id/next_button_imageview")), 10000)
            device.findObject(By.res("com.instagram.android:id/next_button_imageview")).click()
            Thread.sleep(20000)

        }
        //FILTER TRIM COVER Video için

        try {
            if(device.hasObject(By.textContains("COVER"))){

                device.findObject(By.textContains("COVER")).click()
                Thread.sleep(1000)
                device.findObject(By.res("com.instagram.android:id/filmstrip_keyframes_holder")).children.get(0).click()
                Thread.sleep(5000)
                //com.instagram.android:id/filmstrip_keyframes_holder
            }
        }
        catch (ex:java.lang.Exception){
            Log.e("ahmetcan","erro blocked COVER")
        }

        try {

            device.wait(Until.hasObject(By.res("com.instagram.android:id/next_button_imageview")), 10000)
            device.findObject(By.res("com.instagram.android:id/next_button_imageview")).click()
            Thread.sleep(20000)

        }
        catch (ex:java.lang.Exception){
            device.wait(Until.hasObject(By.res("com.instagram.android:id/next_button_imageview")), 10000)
            device.findObject(By.res("com.instagram.android:id/next_button_imageview")).click()
            Thread.sleep(20000)

        }



        if(content!=null){


            try {

                device.wait(Until.hasObject(By.res("com.instagram.android:id/caption_text_view")), 10000)
                device.findObject(By.res("com.instagram.android:id/caption_text_view")).text=content
                Thread.sleep(20000)

            }
            catch (ex:java.lang.Exception){

            }


        }
        try {
            device.wait(Until.hasObject(By.res("com.instagram.android:id/next_button_imageview")),    60000)
            device.findObject(By.res("com.instagram.android:id/next_button_imageview")).click()
            Thread.sleep(20000)

        }
        catch (ex:java.lang.Exception){
            device.wait(Until.hasObject(By.res("com.instagram.android:id/next_button_imageview")),    60000)
            device.findObject(By.res("com.instagram.android:id/next_button_imageview")).click()
            Thread.sleep(20000)
        }

    }
}