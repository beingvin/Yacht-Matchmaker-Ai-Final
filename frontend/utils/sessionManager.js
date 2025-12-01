/**
 * sessionManager.js
 * * This module provides a function to retrieve a stable, persistent user ID 
 * from the browser's localStorage. This ID is essential for maintaining 
 * conversational history with the Python ADK backend.
 */

const STORAGE_KEY = 'yacht_matchmaker_client_id';

/**
 * Retrieves the persistent user ID, generating a new one if it doesn't exist.
 * This ID should be sent with every chat message to the backend.
 * * @returns {string} The stable user ID.
 */
export function getPersistentUserId() {
    // 1. Try to load an existing ID from localStorage
    let userId = localStorage.getItem(STORAGE_KEY);

    if (!userId) {
        // 2. If no ID exists, generate a new unique identifier (UUID-like structure)
        // This pattern ensures a high probability of uniqueness
        userId = 'user-' + Date.now().toString(36) + Math.random().toString(36).substring(2, 9);
        
        // 3. Save the new ID for all future requests
        localStorage.setItem(STORAGE_KEY, userId);

        console.log(`[Session Manager] New User ID generated and stored: ${userId}`);
    } else {
        console.log(`[Session Manager] Reusing stored User ID: ${userId}`);
    }
    
    // 4. Return the guaranteed stable ID
    return userId;
}

// Example usage in your Next.js file (e.g., in a function that sends a message):
/*
async function sendMessage(message) {
    const userId = getPersistentUserId(); // Get the stable ID
    
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: message }) // Send the stable ID
    });
    // ... handle response
}
*/