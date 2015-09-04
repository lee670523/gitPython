import gtk
import jswebkit
from scrapy.http import FormRequest, HtmlResponse
import webkit

import settings

class WebkitDownloader(object):
    def process_request(self, request, spider):
        if spider.name in settings.WEBKIT_DOWNLOADER:
            if type(request) is not FormRequest:
                webview = webkit.WebView()
                webview.connect('load-finished', lambda v, f: gtk.main_quit())
                webview.load_uri(request.url)
                gtk.main()
                js = jswebkit.JSContext(webview.get_main_frame().get_global_context())
                rendered_body = str(js.EvaluateScript('document.body.innerHTML'))
                return HtmlResponse(request.url, body=rendered_body)
            
