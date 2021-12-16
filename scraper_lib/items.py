class LegisItem():
    def __init__(self, url, shorthand):
        self.url = url
        self.shorthand = shorthand
        self.html = None
        self.sl_urls = []
    
    def set_html(self, html):
        self.html = html