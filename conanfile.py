from conans import CMake, ConanFile, tools


class FmtConan(ConanFile):
    name = "fmt"
    version = "4.0.0"
    license = "MIT"
    url = "<Package recipe repository url here, for issues about the package>"
    build_policy = "missing"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "header_only": [True, False],
               "fPIC": [True, False]}
    default_options = "shared=False", "header_only=False", "fPIC=False"
    generators = "cmake"

    def configure(self):
        if self.options.header_only:
            self.settings.clear()
            self.options.remove("shared")
            self.options.remove("fPIC")

    def source(self):
        self.run("git clone https://github.com/fmtlib/fmt.git")
        self.run("cd fmt && git checkout %s" % self.version)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("fmt/CMakeLists.txt", "PROJECT(FMT)", '''PROJECT(FMT)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        if self.options.header_only:
            return
        cmake = CMake(self)
        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        else:
            cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"
        if self.settings.os != "Windows" and self.options.fPIC:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "True"
        cmake.definitions["FMT_TEST"] = "OFF"
        cmake.definitions["FMT_DOCS"] = "OFF"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        
        cmake.configure(source_dir="fmt")
        cmake.build()
        cmake.install()

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.defines.append("FMT_HEADER_ONLY")
        else:
            self.cpp_info.libs.append("fmt")
