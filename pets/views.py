from django.shortcuts import render
from rest_framework.views import APIView, Request, Response, status
from django.shortcuts import get_object_or_404
from pets.models import Pet
from groups.models import Group
from traits.models import Trait
from pets.serializers import PetSerializer
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class PetView(APIView, PageNumberPagination):
    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data_groups = serializer.validated_data.pop('group', None)
        data_traits = serializer.validated_data.pop('traits', None)

        group = Group.objects.filter(scientific_name__iexact = data_groups['scientific_name']).first()

        if not group:
            group = Group.objects.create(**data_groups)

        render_pet = Pet.objects.create(**serializer.validated_data, group = group,)

        for trait_dict in data_traits:
            trait = Trait.objects.filter(name__iexact = trait_dict['name']).first()

            if not trait:
                trait = Trait.objects.create(**trait_dict)

            trait.pets.add(render_pet)

        serializer = PetSerializer(instance=render_pet)

        return Response(serializer.data, status.HTTP_201_CREATED)
    
    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()
        traits = request.query_params.get('trait', None)

        if traits:
            trait = Trait.objects.filter(name__iexact=traits).first()

            if trait:
                pets = Pet.objects.filter(traits=trait).all()

        result = self.paginate_queryset(pets, request)

        serializer = PetSerializer(instance=result, many=True)

        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: id) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(instance=pet)

        return Response(serializer.data, status.HTTP_200_OK)
    
    def delete(self, request: Request, pet_id: id) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    def patch(self, request: Request, pet_id) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        data_groups = serializer.validated_data.pop('group', None)
        data_traits = serializer.validated_data.pop('traits', None)

        if data_groups:
            try:
                group_obj = Group.objects.get(scientific_name__iexact=data_groups['scientific_name'])

            except Group.DoesNotExist:
                group_obj = Group.objects.create(**data_groups)

            pet.group = group_obj
        
        if data_traits:
            trait_obj = []

            for trait_dict in data_traits:
                try:
                    trait = Trait.objects.get(name__iexact=trait_dict['name'])
                
                except Trait.DoesNotExist:
                    trait = Trait.objects.create(**trait_dict)

                trait_obj.append(trait)

            pet.traits.set(trait_obj)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)
        
        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    
            

    


        



        



