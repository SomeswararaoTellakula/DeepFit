import UIKit
import WebKit

/**
 * DeepFitViewController displays the web-based application within the native iOS app.
 * It uses WKWebView for high-performance rendering.
 */
class DeepFitViewController: UIViewController, WKNavigationDelegate {
    var webView: WKWebView!

    override func loadView() {
        let webConfiguration = WKWebViewConfiguration()
        
        // Enable standard web features
        webConfiguration.allowsInlineMediaPlayback = true
        
        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        webView.navigationDelegate = self
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        
        /* 
         * LOAD DEEPFIT URL
         * Simulator: http://localhost:5000
         * Physical Device: http://[YOUR_LAPTOP_IP]:5000
         */
        if let url = URL(string: "http://localhost:5000") {
            let request = URLRequest(url: url)
            webView.load(request)
        }
    }
    
    // Optional: Handle deep links passed from the AppIntent
    func navigateTo(route: String) {
        if let url = URL(string: "http://localhost:5000/\(route)") {
            let request = URLRequest(url: url)
            webView.load(request)
        }
    }
}
