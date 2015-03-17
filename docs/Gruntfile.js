/*
#  Gruntfile
#  Provides configuration for tasks and Grunt extensions
#
#  Copyright © SoftLayer, an IBM Company
#  Code and documentation licensed under MIT
*/

module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON("package.json"),
        site: grunt.file.readYAML("_config.yml"),
        banner: "/* \n" +
                " * \n" +
                " * Boilerplate <%= site.project.version %>, Built on <%= grunt.template.today(\"mm-dd-yyyy\") %>\n" +
                " * Copyright © <%= grunt.template.today(\"yyyy\") %> <%= site.owner.name %>. All rights reserved.\n" +
                " * Code and documentation licensed under <%= site.license.type %>.\n" + " * \n" + " */\n\n",

        shell: {
            bundler: {
                command: ["gem update --system",
                          "gem install bundler",
                          "bundle install --quiet",
                          "rm -r Gemfile.lock"].join("&&"),
                options: {
                    stdout: true
                }
            },
            pygments: {
                command: ["cd assets/packages",
                          "python ez_setup.py",
                          "python get-pip.py",
                          "pip install Pygments",
                          "rm -r setuptools*",
                          "cd ../../"].join("&&"),
                options: {
                    stdout: true
                }
            }
        },
        clean: {
            before: ["public/css/main.css",
                     "public/js/main.js",
                     "public/js/profile.js",
                     "_includes/packages/setuptools*",
                     "validation-*.json",
                     "*.lock"]
        },

        concat: {
            main: {
                options: {
                    banner: "<%= banner %>"
                },
                src: ["plugins/stub.js",
                      "plugins/classify.js",
                      "plugins/toggle.js",
                      "plugins/indexing.js",
                      "plugins/scrollable.js",
                      "plugins/readability.js",
                      "plugins/portfolio.js"],
                dest: "assets/js/main.js"
            }
        },

        uglify: {
            main: {
                options: {
                    banner: "<%= banner %>",
                    report: "min"
                },
                src: "<%= concat.main.dest %>",
                dest: "assets/js/main.js"
            }
        },

        recess: {
            unminify: {
                options: {
                    compile: true,
                    compress: false,
                    banner: "<%= banner %>"
                },
                src: ["less/@import.less"],
                dest: "assets/css/main.css"
            },
            minify: {
                options: {
                    compile: true,
                    compress: true,
                    banner: "<%= banner %>"
                },
                src: ["less/@import.less"],
                dest: "assets/css/main.css"
            }
        },

        jekyll: {
            test: {},
            preview: {
                options: {
                    watch: true,
                    serve: true,
                    baseurl: ["\"\""]
                }
            }
        },

        validation: {
            options: {
                charset: "UTF-8",
                doctype: "HTML5",
                failHard: true,
                reset: true,
                relaxerror: ["Bad value X-UA-Compatible for attribute http-equiv on element meta.",
                             "Element img is missing required attribute src.",
                             "Empty heading",
                             "Bad value button for attribute type on element a: Subtype missing.",
                             "No p element in scope but a p end tag seen.",
                             "Section lacks heading.",
                             "The align attribute on the th element is obsolete.",
                             "The align attribute on the td element is obsolete.",
                             "Illegal character in query: not a URL code point."]
            },
            files: {
                src: ["_site/*.html", "_site/**/*.html"]
            }
        }
    });

    grunt.loadNpmTasks("grunt-contrib-clean");
    grunt.loadNpmTasks("grunt-contrib-concat");
    grunt.loadNpmTasks("grunt-contrib-uglify");
    grunt.loadNpmTasks("grunt-html-validation");
    grunt.loadNpmTasks("grunt-jekyll");
    grunt.loadNpmTasks("grunt-recess");
    grunt.loadNpmTasks("grunt-shell");

    grunt.registerTask("build",        ["clean", "concat", "uglify", "recess:minify"]);
    grunt.registerTask("build:pretty", ["clean", "concat", "recess:unminify"]);
    grunt.registerTask("install",      ["shell:bundler", "shell:pygments"]);
    grunt.registerTask("preview",      ["jekyll:preview"]);
    grunt.registerTask("serve",        ["build", "jekyll:preview"]);
    grunt.registerTask("serve:pretty", ["build:pretty", "jekyll:preview"]);
    grunt.registerTask("test",         ["jekyll:test", "validation"]);
};
