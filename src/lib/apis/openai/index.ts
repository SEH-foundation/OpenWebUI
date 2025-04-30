const OPENAI_API_BASE_URL = 'https://synapticabase-production.up.railway.app';

export const getOpenAIConfig = async (token: string = '') => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/config`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		}
	});
	return res.json();
};

export const updateOpenAIConfig = async (token: string = '', config: any) => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/config/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(config)
	});
	return res.json();
};

export const getOpenAIUrls = async (token: string = '') => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/urls`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		}
	});
	const data = await res.json();
	return data.OPENAI_API_BASE_URLS;
};

export const updateOpenAIUrls = async (token: string = '', urls: string[]) => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/urls/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		},
		body: JSON.stringify({ urls })
	});
	const data = await res.json();
	return data.OPENAI_API_BASE_URLS;
};

export const getOpenAIKeys = async (token: string = '') => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/keys`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		}
	});
	const data = await res.json();
	return data.OPENAI_API_KEYS;
};

export const updateOpenAIKeys = async (token: string = '', keys: string[]) => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/keys/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		},
		body: JSON.stringify({ keys })
	});
	const data = await res.json();
	return data.OPENAI_API_KEYS;
};

export const getOpenAIModels = async (token: string = '', urlIdx?: number) => {
	const url = `${OPENAI_API_BASE_URL}/models${typeof urlIdx === 'number' ? `/${urlIdx}` : ''}`;
	const res = await fetch(url, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		}
	});
	return res.json();
};

export const chatCompletion = async (
	token: string = '',
	body: object
): Promise<[Response | null, AbortController]> => {
	const controller = new AbortController();

	const res = await fetch(`${OPENAI_API_BASE_URL}/chat/completions`, {
		signal: controller.signal,
		method: 'POST',
		headers: {
			Accept: 'application/json',
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(body)
	});

	return [res, controller];
};

export const generateOpenAIChatCompletion = async (token: string = '', body: object) => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/chat/completions`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(body)
	});
	return res.json();
};

export const synthesizeOpenAISpeech = async (
	token: string = '',
	speaker: string = 'alloy',
	text: string = '',
	model: string = 'tts-1'
) => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/audio/speech`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			model,
			input: text,
			voice: speaker
		})
	});
	return res.json();
};

// ВАЖНО: эта функция нужна для корректного импорта в index.ts OpenWebUI
export const getOpenAIModelsDirect = async (url: string, key: string) => {
	const res = await fetch(`${url}/models`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			Authorization: `Bearer ${key}`
		}
	});
	if (!res.ok) {
		throw new Error('Failed to fetch models');
	}
	return res.json();
};

export const verifyOpenAIConnection = async (token: string = '') => {
	const res = await fetch(`${OPENAI_API_BASE_URL}/config`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { Authorization: `Bearer ${token}` })
		}
	});
	return res.ok;
};

