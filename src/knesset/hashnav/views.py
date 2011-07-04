import os

class ClassBasedView(object):
    def __call__(self, request, **kwargs):
        self.pre(request, **kwargs)       
        ret = self.render(request, **kwargs)
        return self.post(request, ret, **kwargs)

    def pre (self, request, **kwargs):
        pass

    def post(self, request, ret, **kwargs):
        return ret
        
    def full_to_part(self, template_name):
        return os.path.join(os.path.dirname(template_name),
                            "_%s" % os.path.basename(template_name))

