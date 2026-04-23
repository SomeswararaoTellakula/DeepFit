import AppIntents

/**
 * DeepFitShortcuts makes the intent discoverable by Siri automatically.
 * No manual user setup is required in the Shortcuts app.
 */
struct DeepFitShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OpenDeepFitIntent(),
            phrases: [
                "Open \(.applicationName)",
                "Start my workout in \(.applicationName)",
                "Get fit with \(.applicationName)"
            ],
            shortTitle: "Open DeepFit",
            systemImageName: "figure.run"
        )
    }
}
