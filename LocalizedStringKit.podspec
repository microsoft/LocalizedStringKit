Pod::Spec.new do |s|
  s.name             = 'LocalizedStringKit'
  s.version          = '0.2.5'
  s.summary          = 'Generate .strings files directly from your code'

  s.description      = <<-DESC
  LocalizedStringKit is a tool that lets you write English strings directly into your source code and generate the required .strings files later. No more manually managing string keys or remembering to add them to the strings file later.
                       DESC

  s.homepage         = 'https://github.com/microsoft/LocalizedStringKit'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.author           = { 'Dale Myers' => 'dalemy@microsoft.com' }
  s.source           = { :git => 'https://github.com/microsoft/LocalizedStringKit.git', :tag => s.version.to_s }

  s.ios.deployment_target = '13.0'

  s.swift_versions = ['5.0']

  # The runtime is implemented in Swift with a thin Objective-C facade that
  # provides the historical `Localized(...)` free functions. CocoaPods builds
  # both languages into a single mixed module, so the facade reaches the Swift
  # implementation through the generated `-Swift.h` header (see LSK_MIXED_MODULE).
  s.source_files = 'Sources/LocalizedStringKit/**/*.{h,m}', 'Sources/LocalizedStringKitCore/**/*.swift'
  s.public_header_files = 'Sources/LocalizedStringKit/include/**/*.h'

  s.pod_target_xcconfig = {
    'GCC_PREPROCESSOR_DEFINITIONS' => '$(inherited) LSK_MIXED_MODULE=1'
  }
end
