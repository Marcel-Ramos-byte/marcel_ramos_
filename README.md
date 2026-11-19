# Marcel Labs

Portal estático de ferramentas, pronto para hospedagem em GitHub Pages ou qualquer servidor de arquivos estáticos. Sem instalação de dependências e sem backend.

- `index.html`: página inicial e busca de ferramentas.
- `caldeira/`: simulador THERMO, com menu recolhível.
- `alarme_de_incendio/`: laboratório de detecção, com menu recolhível. O endereço antigo `laboratorio_simplex_compacto.html` continua disponível.
- `clima/`: previsão meteorológica; catálogo local em `dados/municipios.json`.
- `assets/css/navigation.css`: estilos isolados da navegação compartilhada.
- `scripts/build.py`: valida links locais e gera `dist/` apenas com arquivos públicos.

## Executar e verificar

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

Abra `http://localhost:8000`. Confira os menus, busca, controles dos simuladores e seleção de estado/município. A previsão precisa de internet para consultar a API Open-Meteo.

## Publicar

Envie este projeto para um repositório GitHub. Em **Settings → Pages → Build and deployment**, selecione **GitHub Actions**. O workflow `.github/workflows/pages.yml` valida e publica os arquivos ao receber alterações em `main` ou `master`; também permite execução manual. Os caminhos relativos funcionam tanto no domínio principal quanto em um subdiretório de repositório.

Para outra hospedagem, publique o conteúdo de `dist/` após executar o build. Configure o servidor para servir `index.html` como índice de pastas e `404.html` em erros 404.

## Manutenção

Ao alterar o simulador de alarme, mantenha `alarme_de_incendio/index.html` e o arquivo do endereço antigo idênticos. Nas simulações, o menu fica fixo no canto inferior direito e pode ser recolhido; seus estilos usam classes próprias para preservar os layouts existentes. Não há credenciais necessárias para executar o portal.
