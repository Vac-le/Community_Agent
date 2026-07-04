import { streamPost } from './streamRequest';
import { BASE_URL } from '@/main.js'

export const callAgentStream = async (userInput, sessionId = '') => {
  const url = BASE_URL + '/user/agent/chat/stream';

  const requestData = {
    message: userInput,
    sessionId
  };

  try {
    const response = await streamPost(url, requestData);
    return response;
  } catch (error) {
    throw new Error(`调用Agent流式接口失败: ${error.message}`);
  }
};
