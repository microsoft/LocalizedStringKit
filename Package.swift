// swift-tools-version:5.2

import PackageDescription

let package = Package(
    name: "LocalizedStringKit",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15),
        .tvOS(.v13),
        .watchOS(.v6),
    ],
    products: [
        .library(
            name: "LocalizedStringKit",
            targets: ["LocalizedStringKit"]),
    ],
    dependencies: [],
    targets: [
        // The Swift implementation.
        .target(
            name: "LocalizedStringKitCore",
            dependencies: []),
        // The public, historically-compatible Objective-C facade. It exposes
        // the `Localized(...)` family of C free functions (usable from both
        // Objective-C and Swift) and forwards to the Swift implementation.
        .target(
            name: "LocalizedStringKit",
            dependencies: ["LocalizedStringKitCore"]),
        .testTarget(
            name: "LocalizedStringKitTests",
            dependencies: ["LocalizedStringKit"]),
    ]
)
