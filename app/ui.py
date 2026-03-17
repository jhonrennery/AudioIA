from __future__ import annotations

import gradio as gr

from .languages import LANGUAGE_OPTIONS, REWRITE_STYLES
from .services import create_download_bundle, process_audio


APP_CSS = """
body {
    background:
        radial-gradient(circle at top left, rgba(232, 119, 34, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(13, 148, 136, 0.18), transparent 30%),
        linear-gradient(180deg, #f8f1e6 0%, #f3eadc 45%, #efe4d4 100%);
}

.gradio-container {
    max-width: 1200px !important;
}

.hero {
    padding: 28px;
    border: 1px solid rgba(88, 62, 38, 0.12);
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(255, 250, 242, 0.96), rgba(248, 237, 219, 0.9));
    box-shadow: 0 18px 60px rgba(92, 64, 39, 0.10);
}

.hero h1 {
    margin: 0;
    font-size: 3rem;
    line-height: 1;
    letter-spacing: -0.04em;
}

.hero p {
    margin: 12px 0 0;
    font-size: 1.05rem;
}

.hero-grid {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 20px;
    align-items: end;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 18px;
}

.pill {
    display: inline-flex;
    align-items: center;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(88, 62, 38, 0.12);
    font-size: 0.95rem;
}

.hero-side {
    padding: 18px;
    border-radius: 22px;
    background: rgba(110, 70, 34, 0.06);
    border: 1px solid rgba(88, 62, 38, 0.12);
}

.hero-side strong {
    display: block;
    margin-bottom: 8px;
}

.panel {
    border: 1px solid rgba(88, 62, 38, 0.12);
    border-radius: 24px;
    background: rgba(255, 252, 247, 0.86);
    box-shadow: 0 12px 40px rgba(92, 64, 39, 0.08);
}

.section-title {
    margin: 0 0 6px;
    font-size: 1.2rem;
}

.section-copy {
    margin: 0;
    opacity: 0.82;
}

.result-card {
    min-height: 100%;
}

.status-box {
    padding: 14px 16px;
    border-radius: 18px;
    background: rgba(13, 148, 136, 0.08);
    border: 1px solid rgba(13, 148, 136, 0.15);
}

@media (max-width: 900px) {
    .hero-grid {
        grid-template-columns: 1fr;
    }

    .hero h1 {
        font-size: 2.3rem;
    }
}
"""


APP_THEME = gr.themes.Soft(
    primary_hue="amber",
    secondary_hue="teal",
    neutral_hue="stone",
    font=[gr.themes.GoogleFont("Merriweather"), "serif"],
    font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "monospace"],
).set(
    body_background_fill="#efe4d4",
    block_background_fill="#fffaf2",
    block_border_color="#dcc7aa",
    block_label_text_color="#4b3828",
    button_primary_background_fill="#c96f1d",
    button_primary_background_fill_hover="#af5f19",
    button_primary_text_color="#fffaf2",
    checkbox_label_text_color="#4b3828",
    input_background_fill="#fffdf8",
)


OUTPUT_KEYS = [
    "transcript",
    "rewritten",
    "translated",
    "translated_audio",
    "download_file",
    "status",
]


def _empty_result(status: str):
    return {
        "transcript": "",
        "rewritten": "",
        "translated": "",
        "translated_audio": None,
        "download_file": None,
        "status": status,
    }


def _run_pipeline(audio_path, source_label, rewrite_label, target_label, create_audio):
    if not audio_path:
        return _empty_result("Envie ou grave um audio para continuar.")

    transcript, rewritten, translated, translated_audio = process_audio(
        audio_path=audio_path,
        source_language=LANGUAGE_OPTIONS[source_label],
        rewrite_style=REWRITE_STYLES[rewrite_label],
        target_language=LANGUAGE_OPTIONS[target_label],
        generate_audio=create_audio,
    )

    status = "Processamento concluido com sucesso."
    if create_audio and not translated_audio:
        status += " O audio traduzido nao foi gerado porque gTTS nao esta disponivel."

    return {
        "transcript": transcript,
        "rewritten": rewritten,
        "translated": translated,
        "translated_audio": translated_audio,
        "download_file": create_download_bundle(
            transcript,
            rewritten,
            translated,
            translated_audio,
        ),
        "status": status + " Baixe o pacote com os resultados na secao de downloads.",
    }


def _result_to_tuple(result: dict[str, object]):
    return tuple(result[key] for key in OUTPUT_KEYS)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AudioIA", theme=APP_THEME, css=APP_CSS) as app:
        gr.Markdown(
            """
            <div class="hero">
              <div class="hero-grid">
                <div>
                  <h1>AudioIA</h1>
                  <p>Grave sua voz, limpe a transcricao, traduza para outros idiomas e gere um novo audio com um fluxo simples e direto.</p>
                  <div class="pill-row">
                    <span class="pill">Transcricao inteligente</span>
                    <span class="pill">Reescrita clara</span>
                    <span class="pill">Traducao multilíngue</span>
                    <span class="pill">Modo ao vivo</span>
                  </div>
                </div>
                <div class="hero-side">
                  <strong>Fluxo rapido</strong>
                  Grave ou envie um audio, ajuste o tom da reescrita e receba a versao traduzida pronta para leitura, escuta e download.
                </div>
              </div>
            </div>
            """
        )

        last_live_audio = gr.State("")

        with gr.Row():
            with gr.Column(scale=5):
                with gr.Group(elem_classes=["panel"]):
                    gr.Markdown(
                        """
                        <h3 class="section-title">Entrada de voz</h3>
                        <p class="section-copy">Use upload ou microfone. No modo ao vivo, cada nova gravacao e processada automaticamente.</p>
                        """
                    )
                    audio_input = gr.Audio(
                        sources=["upload", "microphone"],
                        type="filepath",
                        label="Audio de entrada",
                    )

            with gr.Column(scale=4):
                with gr.Group(elem_classes=["panel"]):
                    gr.Markdown(
                        """
                        <h3 class="section-title">Controles</h3>
                        <p class="section-copy">Defina idioma, estilo de reescrita e como a saida deve ser entregue.</p>
                        """
                    )
                    source_language = gr.Dropdown(
                        choices=list(LANGUAGE_OPTIONS.keys()),
                        value="Auto detectar",
                        label="Idioma de origem",
                    )
                    rewrite_style = gr.Dropdown(
                        choices=list(REWRITE_STYLES.keys()),
                        value="Natural",
                        label="Estilo da reescrita",
                    )
                    target_language = gr.Dropdown(
                        choices=[item for item in LANGUAGE_OPTIONS.keys() if item != "Auto detectar"],
                        value="Ingles",
                        label="Idioma de destino",
                    )
                    with gr.Row():
                        generate_audio = gr.Checkbox(
                            value=True,
                            label="Gerar audio traduzido",
                        )
                        live_mode = gr.Checkbox(
                            value=True,
                            label="Modo ao vivo",
                            info="Processa automaticamente cada nova gravacao do microfone.",
                        )
                    run_button = gr.Button("Processar audio", variant="primary", size="lg")

        with gr.Row():
            with gr.Column(scale=4):
                with gr.Group(elem_classes=["panel", "result-card"]):
                    gr.Markdown("### Transcricao")
                    transcript_output = gr.Textbox(
                        label="Texto reconhecido",
                        lines=8,
                        placeholder="A transcricao da sua fala aparece aqui.",
                    )
            with gr.Column(scale=4):
                with gr.Group(elem_classes=["panel", "result-card"]):
                    gr.Markdown("### Reescrita")
                    rewritten_output = gr.Textbox(
                        label="Versao refinada",
                        lines=8,
                        placeholder="O texto reescrito com mais clareza aparece aqui.",
                    )
            with gr.Column(scale=4):
                with gr.Group(elem_classes=["panel", "result-card"]):
                    gr.Markdown("### Traducao")
                    translated_output = gr.Textbox(
                        label="Saida no idioma final",
                        lines=8,
                        placeholder="A traducao final aparece aqui.",
                    )

        with gr.Row():
            with gr.Column(scale=5):
                with gr.Group(elem_classes=["panel"]):
                    gr.Markdown("### Audio traduzido")
                    translated_audio_output = gr.Audio(label="Escute ou baixe o resultado")
                    download_output = gr.File(label="Download dos resultados")
            with gr.Column(scale=4):
                with gr.Group(elem_classes=["panel"]):
                    gr.Markdown(
                        """
                        ### Dicas de uso
                        - Fale em blocos curtos para respostas mais estaveis.
                        - Use `Natural` para conversas e `Profissional` para apresentacoes.
                        - Mantenha `Modo ao vivo` ligado para repetir o fluxo com mais rapidez.
                        - Use o pacote de download para salvar textos e audio gerados.
                        """
                    )
                    status_output = gr.Markdown(
                        value="Abra a ferramenta em `http://127.0.0.1:7860` quando estiver rodando fora do Docker.",
                        elem_classes=["status-box"],
                    )

        def run_pipeline(audio_path, source_label, rewrite_label, target_label, create_audio):
            try:
                result = _run_pipeline(
                    audio_path,
                    source_label,
                    rewrite_label,
                    target_label,
                    create_audio,
                )
            except Exception as exc:
                raise gr.Error(str(exc)) from exc

            return _result_to_tuple(result)

        def auto_process(audio_path, source_label, rewrite_label, target_label, create_audio, enabled, last_path):
            if not enabled:
                return (
                    gr.skip(),
                    gr.skip(),
                    gr.skip(),
                    gr.skip(),
                    gr.skip(),
                    "Modo ao vivo desativado. Use o botao Processar audio.",
                    last_path,
                )

            if not audio_path:
                return gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), last_path

            if audio_path == last_path:
                return gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), last_path

            try:
                result = _run_pipeline(
                    audio_path,
                    source_label,
                    rewrite_label,
                    target_label,
                    create_audio,
                )
            except Exception as exc:
                raise gr.Error(str(exc)) from exc

            result["status"] = "Modo ao vivo: nova gravacao processada. " + str(result["status"])
            return (*_result_to_tuple(result), audio_path)

        run_button.click(
            fn=run_pipeline,
            inputs=[audio_input, source_language, rewrite_style, target_language, generate_audio],
            outputs=[
                transcript_output,
                rewritten_output,
                translated_output,
                translated_audio_output,
                download_output,
                status_output,
            ],
        )

        audio_input.change(
            fn=auto_process,
            inputs=[
                audio_input,
                source_language,
                rewrite_style,
                target_language,
                generate_audio,
                live_mode,
                last_live_audio,
            ],
            outputs=[
                transcript_output,
                rewritten_output,
                translated_output,
                translated_audio_output,
                download_output,
                status_output,
                last_live_audio,
            ],
        )

    return app
