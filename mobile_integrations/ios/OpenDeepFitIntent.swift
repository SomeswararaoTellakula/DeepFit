import AppIntents
import UIKit

/**
 * OpenDeepFitIntent defines the voice command for Siri.
 * Users can say "Hey Siri, Open DeepFit".
 */
struct OpenDeepFitIntent: AppIntent {
    static var title: LocalizedStringResource = "Open DeepFit"
    static var description = IntentDescription("Opens the DeepFit application to start your fitness tracking.")
    
    // This tells the system to bring the app to the foreground when this intent is run
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult {
        // Logic to execute when the app is opened via Siri
        // You can use deep links or notification observers to navigate
        print("Siri triggered OpenDeepFitIntent")
        
        return .result()
    }
}
