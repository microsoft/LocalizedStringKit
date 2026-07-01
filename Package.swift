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
        .target(
            name: "LocalizedStringKit",
            dependencies: []),
        .testTarget(
            name: "LocalizedStringKitTests",
            dependencies: ["LocalizedStringKit"]),
    ]
)
