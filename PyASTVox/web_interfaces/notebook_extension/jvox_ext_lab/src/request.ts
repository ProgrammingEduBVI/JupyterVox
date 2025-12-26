import { URLExt } from '@jupyterlab/coreutils';

import { ServerConnection } from '@jupyterlab/services';

/**
 * Call the server extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
export async function requestAPI(
  endPoint = '',
  init: RequestInit = {}
): Promise<Response> {
    // Make request to Jupyter API
    const settings = ServerConnection.makeSettings();
    const requestUrl = URLExt.join(
	settings.baseUrl,
	'jvox-lab-ext', // our server extension's API namespace
	endPoint
    );
    
    let response: Response;
    try {
	response = await ServerConnection.makeRequest(requestUrl, init, settings);
    } catch (error) {
	throw new ServerConnection.NetworkError(error as any);
    }
    
    // let data: any = await response.text();
    
    // if (data.length > 0) {
    //   try {
    //     data = JSON.parse(data);
    //   } catch (error) {
    //     console.log('Not a JSON response body.', response);
    //   }
    // }

    if (!response.ok) {
	// throw new ServerConnection.ResponseError(response, data.message || data);
	
	// Even if it's an error, the body might contain a JSON error message
	const errorData = await response.json().catch(() => ({})); 
	throw new Error(errorData.message || `Server error: ${response.status}`);
    }
    
    return response;
    
}
