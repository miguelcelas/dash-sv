# Semiárido Vivo Dashboard

Dashboard interativo para curadoria de notícias do Semiárido brasileiro, com filtros por estado, tema e data (somente conteúdos de **01/01/2026 em diante**).

## Como executar localmente

Como é uma versão estática, basta abrir `index.html` no navegador.

Opção com servidor local:

```bash
python3 -m http.server 8080
```

Depois acesse: `http://localhost:8080`

## Estrutura

- `index.html`: layout do dashboard
- `styles.css`: tema e tipografia (Adobe Fonts Typekit)
- `app.js`: carregamento, filtros e renderização
- `data/sources.json`: cadastro de fontes (fácil inclusão)
- `data/news.json`: banco de notícias (newsletter + dashboard)
- `scripts/validate_news.py`: validação de data mínima e campos obrigatórios

## Como incluir novas fontes

Edite `data/sources.json` adicionando um novo objeto em `sources`:

```json
{
  "name": "Nome da fonte",
  "state": "BA",
  "region": "Semiárido",
  "type": "independente",
  "url": "https://exemplo.com",
  "active": true
}
```

## Como inserir notícias

Adicione itens em `data/news.json` no array `items`:

```json
{
  "id": "2026-0001",
  "title": "Título da notícia",
  "summary": "Resumo com até 180 caracteres.",
  "source": "Nome do veículo",
  "url": "https://link-da-materia",
  "paywall": false,
  "state": "BA",
  "themes": ["clima", "políticas públicas"],
  "published_at": "2026-01-15"
}
```

## Formato para newsletter

Cada entrada já é exibida no padrão:

- ✏️ título/manchete
- 👉🏾 resumo de até 180 caracteres
- 📰 nome do veículo
- 🔗 link da matéria + `🔒` quando houver paywall

## Validação

```bash
python3 scripts/validate_news.py
```

A validação garante:

- data >= `2026-01-01`
- resumo com até 180 caracteres
- campos obrigatórios preenchidos


## Sobre os filtros (importante)

Se aparecerem poucas notícias, o dashboard aplica estes critérios ao mesmo tempo:

1. Só mostra notícias com `published_at >= 2026-01-01`.
2. Data inicial padrão começa em `2026-01-01`.
3. Estado e tema podem reduzir ainda mais (quando selecionados).
4. Se marcar "Ocultar matérias com paywall", itens com `paywall: true` saem da lista.

Além disso, a base inicial de exemplo veio com apenas 2 notícias em `data/news.json`.


## Implementação de atualização diária (ao vivo)

1. Cadastre os feeds RSS/Atom por fonte em `data/sources.json` no campo `feeds`.
2. Rode o coletor para atualizar `data/news.json`:

```bash
python3 scripts/update_news.py
```

3. Valide o resultado:

```bash
python3 scripts/validate_news.py
```

### Automação diária (GitHub Actions)

Crie workflow para execução diária (cron) do coletor + commit automático do `data/news.json`.

Exemplo de agenda: `0 10 * * *` (10:00 UTC).
