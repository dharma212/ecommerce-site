from .models import Category

def category_context(request):
    return {
        'header_categories': Category.objects.all().prefetch_related('subcategories')
    }