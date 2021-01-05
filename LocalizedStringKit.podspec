Pod::Spec.new do |s|
  s.name             = 'LocalizedStringKit'
  s.version          = '0.2.4'
  s.summary          = 'Generate .strings files directly from your code'

  s.description      = <<-DESC
  LocalizedStringKit is a tool that lets you write English strings directly into your source code and generate the required .strings files later. No more manually managing string keys or remembering to add them to the strings file later.
                       DESC

  s.homepage         = 'https://github.com/microsoft/LocalizedStringKit'
  s.license          = { :type => 'MIT', :file => 'LICENSE' }
  s.author           = { 'Dale Myers' => 'dalemy@microsoft.com' }
  s.source           = { :git => 'https://github.com/microsoft/LocalizedStringKit.git', :tag => s.version.to_s }

  s.ios.deployment_target = '9.0'

  s.source_files = 'Sources/LocalizedStringKit/**/*'
  
  s.public_header_files = 'Sources/LocalizedStringKit/include/**/*.h'
end
