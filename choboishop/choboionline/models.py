from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name="Category Name"),
        slug=models.SlugField(max_length=200, unique=True, verbose_name="Category Slug"),
    )

    class Meta:
       # ordering = ['name']
       # indexes = [
       #    models.Index(fields=['name']),
       # ]
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL for a category instance.
        """
        return reverse(
            'choboionline:product_list_by_category', args=[self.slug]
        )

    def __str__(self):
        """
        Returns a human-readable string representation of the model.
        """
        return self.name


class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200),
        description=models.TextField(blank=True)
    )
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name="Category"
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        blank=True,
        verbose_name="Product Image"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Price"
    )
    available = models.BooleanField(default=True, verbose_name="Available")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
       # ordering = ['name']
        indexes = [
          #  models.Index(fields=['id', 'slug']),
          #  models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def get_absolute_url(self):
        """
        Returns the absolute URL for a product instance.
        """
        return reverse('choboionline:product_detail', args=[self.id, self.slug])

    def __str__(self):
        """choboionline:''product_detail', args=[self.id]
        Returns a human-readable string representation of the model.
        """
        return self.name
