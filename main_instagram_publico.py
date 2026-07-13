from scrapers.instagram.scraper_publico import scrape_instagram_publico
import json

def main():
    hashtag = input("🔍 Hashtag a buscar (ej: psytrance): ") or "psytrance"
    print(f"\n🔍 Buscando posts con #{hashtag}...")
    
    posts = scrape_instagram_publico(hashtag, max_posts=15)
    
    print(f"\n📊 Encontrados {len(posts)} posts:")
    for i, post in enumerate(posts, 1):
        print(f"   {i}. {post['nombre']}")
    
    # Guardar
    with open('data/instagram_publico.json', 'w') as f:
        json.dump(posts, f, indent=2)
    print(f"\n✅ Guardado en data/instagram_publico.json")

if __name__ == '__main__':
    main()
