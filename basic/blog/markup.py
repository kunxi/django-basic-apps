from django.utils.html import linebreaks, urlize

def wordpress_renderer(markup):
    rendered = markup
    try:
        import pygments
        PYGMENTS_INSTALLED = True
        from pygments import lexers, formatters
        import re
        regex = re.compile(r'<code(.*?)>(.*?)</code>', re.DOTALL) 

        def pygmentize(value): 
            ''' 
            Finds all <code class="python"></code> blocks in a text block and replaces it with 
            pygments-highlighted html semantics. It relies that you provide the format of the 
            input as class attribute.

            Inspiration:  http://www.djangosnippets.org/snippets/25/
            Updated by: Samualy Clay

            '''
            last_end = 0 
            to_return = '' 
            found = 0
            for match_obj in regex.finditer(value): 
                code_class = match_obj.group(1) 
                code_string = match_obj.group(2) 
                if code_class.find('class') >= 0:
                    language = re.split(r'"|\'', code_class)[1] 
                    lexer = lexers.get_lexer_by_name(language) 
                else: 
                    try: 
                        lexer = lexers.guess_lexer(str(code_string)) 
                    except ValueError: 
                        lexer = lexers.PythonLexer() 
                pygmented_string = pygments.highlight(code_string, lexer, formatters.HtmlFormatter()) 
                to_return = to_return + value[last_end:match_obj.start(0)] + pygmented_string 
                last_end = match_obj.end(0) 
                found = found + 1 
            to_return = to_return + value[last_end:] 
            return to_return
        rendered = pygmentize(rendered)

    except ImportError:
        PYGMENTS_INSTALLED = False

    return linebreaks(rendered)
