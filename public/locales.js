const locales = {
	"en": {
		"connecting": "connecting...",
		"enter_key": "Enter your key",
		"minutes": "minutes",
		"open_game": "Open game",
		"send": "Send",
		"soft_input": "Choose XML files to upload",
		"soft_ok": "saved",
		"soft_not_ok": "failed to send",
		"start": "Starting...",
		"temp_block": "temporarily blocked due to many login attemps",
		"token": "Your token has been generated and will be expired in",
		"hts": "How to start"
	},
	"es": {
		"connecting": "conectando...",
		"enter_key": "Inserta tu llave",
		"minutes": "minutos",
		"open_game": "Abrir juego",
		"send": "Enviar",
		"soft_input": "Seleccione archivos XML para cargar",
		"soft_ok": "guardado",
		"soft_not_ok": "error al enviar",
		"start": "Inicializando...",
		"temp_block": "bloqueado temporalmente debido a muchos intentos de login",
		"token": "Tú token ha sido generado y será expirado en",
		"hts": "Cómo abrir"
	},
	"pt": {
		"connecting": "conectando...",
		"enter_key": "Insira sua chave",
		"minutes": "minutos",
		"open_game": "Abrir jogo",
		"send": "Enviar",
		"soft_input": "Selecione arquivos XML para enviar",
		"soft_ok": "salvo",
		"soft_not_ok": "erro ao enviar",
		"start": "Iniciando...",
		"temp_block": "bloqueado temporariamente devido a muitas tentativas de login",
		"token": "Seu token foi gerado e irá expirar em",
		"hts": "Como abrir"
	}
}

const language = navigator.language.split("-")[0];
const translate = function(key) {
	if (language in locales) {
		if (key in locales[language]) {
			return locales[language][key];
		}
	}

	return locales.en[key] || key;
}