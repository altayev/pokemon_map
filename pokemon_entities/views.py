import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = "https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832&fill=transparent"


def add_pokemon(folium_map, lat, lon, name, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        tooltip=name,
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemon_entities = PokemonEntity.objects.all()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.Lat, pokemon_entity.Lon,
            pokemon_entity.Pokemon.title, request.build_absolute_uri(pokemon_entity.Pokemon.images.url)) 

    pokemons = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': pokemon.images.url,
            'title_ru': pokemon.title,
        })

    return render(request, "mainpage.html", context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        if pokemon.id != int(pokemon_id):
            continue
        pokemon_characteristics = {
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'img_url': request.build_absolute_uri(pokemon.images.url),
        'description': pokemon.description,
        'entities': pokemon.pokemon_entity.all(),
        }
        if pokemon.next_evolution:
            pokemon_characteristics['next_evolution'] = {
            "title_ru": pokemon.next_evolution.title,
            "pokemon_id": pokemon.next_evolution.id,
            "img_url": request.build_absolute_uri(pokemon.next_evolution.images.url)
            }
        
        try:
            previous_evolution = pokemon.previous_evolution.get()
            pokemon_characteristics['previous_evolution'] = {
            "title_ru": previous_evolution.title,
            "pokemon_id": previous_evolution.id,
            "img_url": request.build_absolute_uri(previous_evolution.images.url)
            }
        except Pokemon.DoesNotExist:
            pass

        requested_pokemon = pokemon_characteristics
        break
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')


    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon['entities']:
        add_pokemon(
            folium_map, pokemon_entity.Lat, pokemon_entity.Lon,
            pokemon_entity.Pokemon.title, request.build_absolute_uri(pokemon_entity.Pokemon.images.url))

    return render(request, "pokemon.html", context={'map': folium_map._repr_html_(),
                                                    'pokemon': pokemon_characteristics})
