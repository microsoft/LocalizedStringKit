// swift-tools-version:5.2

import PackageDescription

let package = Package(
    name: "LocalizedStringKit",
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
