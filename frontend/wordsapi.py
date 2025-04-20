import aiohttp

async def get_context(word: str):
    url = "https://api.urbandictionary.com/v0/define"
    params = {"term": word}
    top_n = 4
    text = ''
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch definitions: HTTP {response.status}")
            data = await response.json()
            definitions = data.get("list", [])

            # Sort by thumbs up
            sorted_defs = sorted(definitions, key=lambda d: d["thumbs_up"], reverse=True)

            # Filter out super short or suspicious entries
            clean_defs = [
                d["definition"].strip().replace('[', '').replace(']', '')
                for d in sorted_defs
                if len(d["definition"].strip()) > 10
            ]
            
            for definition in clean_defs[:top_n]:
                text += f'- {definition[0].upper() + definition[1:]}\n'
                
            return '<b>Определения:</b>\n\n' + text if len(text) > 0 else '<b>Определений не найдено(((</b>'
