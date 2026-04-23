/*
 * AndroidManifest.xml Snippet
 * Add this to your <activity> tag for MainActivity
 */

/*
<activity android:name=".MainActivity" ...>
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
    
    <!-- Link to the shortcuts.xml file -->
    <meta-data
        android:name="android.app.shortcuts"
        android:resource="@xml/shortcuts" />
</activity>
*/

package com.deepfit.app

import android.content.Intent
import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import android.util.Log
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize WebView to display the DeepFit web app
        webView = WebView(this)
        setContentView(webView)

        val settings: WebSettings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true // Required for modern web apps
        settings.loadWithOverviewMode = true
        settings.useWideViewPort = true

        webView.webViewClient = WebViewClient()
        
        /* 
         * LOAD DEEPFIT URL
         * Emulator: http://10.0.2.2:5000
         * Physical Device: http://[YOUR_LAPTOP_IP]:5000
         */
        webView.loadUrl("http://10.0.2.2:5000") 

        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        intent?.let {
            if (it.action == Intent.ACTION_VIEW) {
                val feature = it.getStringExtra("feature")
                Log.d("DeepFit", "Received Google Assistant Intent. Feature: $feature")
                
                if (!feature.isNullOrEmpty()) {
                    Toast.makeText(this, "Opening feature: $feature", Toast.LENGTH_SHORT).show()
                    // Navigate the webView to a specific route if needed
                    // webView.loadUrl("http://10.0.2.2:5000/$feature")
                }
            }
        }
    }
}

