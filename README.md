# 📺 VLC TV Remote

Controle o VLC Media Player pelo celular através da rede Wi-Fi local.

O **VLC TV Remote** transforma o computador em uma espécie de central de TV: o VLC reproduz os vídeos no PC enquanto o celular funciona como um controle remoto.

Você pode trocar de episódio, pausar, avançar ou voltar 30 segundos, controlar o volume, ativar mudo, entrar em tela cheia e acompanhar qual vídeo está sendo reproduzido.

---

## ✨ Recursos

- 📱 Controle pelo celular
- ▶️ Reproduzir / pausar
- ⏭️ Próximo episódio
- ⏮️ Episódio anterior
- ⏩ Avançar 30 segundos
- ⏪ Voltar 30 segundos
- 🔊 Controle de volume
- 🔇 Modo mudo
- ⛶ Tela cheia
- 📊 Barra de progresso
- ⏱️ Tempo atual e duração do vídeo
- 🎬 Exibição do nome do vídeo/episódio atual
- 📋 Lista de episódios da playlist do VLC
- ▶️ Destaque automático do episódio que está sendo reproduzido
- 📡 Funciona pela rede Wi-Fi local
- 🖥️ Compatível com Windows
- 🚫 Não precisa instalar aplicativo no celular
- 🌐 Funciona diretamente pelo navegador do celular

---

# 🖥️ Como funciona

O projeto utiliza duas partes principais:

```text
             📱 CELULAR
                 │
                 │ Wi-Fi
                 ▼
        ┌─────────────────┐
        │   VLC TV Remote │
        │   Controle Web  │
        └────────┬────────┘
                 │
                 │ HTTP :8787
                 ▼
        ┌─────────────────┐
        │       PC        │
        │                 │
        │      VLC        │
        └─────────────────┘