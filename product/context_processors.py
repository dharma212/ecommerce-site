from .models import Category

def category_context(request):
    # આ લાઈન ડેટાબેઝમાંથી બધી કેટેગરી અને તેની સબ-કેટેગરી લઈ આવશે
    return {
        'header_categories': Category.objects.all().prefetch_related('subcategories')
    }