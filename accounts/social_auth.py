from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from typing import Dict, Tuple, Optional
import logging
from accounts.models import Profile
from wallet.models import Wallet
from django.db import transaction as db_transaction
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)



class GoogleAuth:

    @staticmethod
    def _extract_user_data(idinfo: Dict) -> Dict:
        """Helper to safely extract and format user data from verified ID token payload."""
        return {
            'email': idinfo.get('email'),
            'email_verified': idinfo.get('email_verified', False),
            'given_name': idinfo.get('given_name', ''),
            'family_name': idinfo.get('family_name', ''),
            'picture': idinfo.get('picture', ''),
            'sub': idinfo.get('sub'), # Google's unique user ID
        }

    @staticmethod
    def verify_id_token(token: str) -> Tuple[bool, str | Dict]:
        """
        Forces the specific Google verification error to be logged.
        """
        try:
            # 1. Verification Attempt
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID 
            )
            
            # 2. Verify the issuer (iss)
            if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error("Invalid issuer provided in token.")
                return False, "Invalid token issuer"
            
            # 3. Success (If no exception was raised)
            user_data = GoogleAuth._extract_user_data(idinfo)
            logger.info(f"Successfully verified ID token for: {user_data['email']}")
            return True, user_data
            
        except ValueError as e:
            # 🎯 CATCH 1: This is the most likely error (Audience, Expiry, etc.)
            error_message = f"Google ID token validation failed: {str(e)}"
            logger.error(error_message)
            return False, error_message
            
        except Exception as e:
            # 🎯 CATCH 2: For any other unexpected error
            error_message = "Authentication failed unexpectedly. Check dependencies or clock sync."
            logger.error(f"Unexpected error during Google ID token authentication: {str(e)}", exc_info=True)
            return False, wallet_error_message
    
    @staticmethod
    def exchange_code_for_user_data(authorization_code: str, redirect_uri: str) -> Tuple[bool, str | Dict]:
        """
        🔐 Handles the traditional Authorization Code Flow (Server-side flow).
        Exchanges the code for tokens and then verifies the resulting ID token.
        (Included for completeness, but not used in your current view)
        """
        TOKEN_URL = "https://oauth2.googleapis.com/token"

        try:
            client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)
            if not client_secret:
                logger.error("GOOGLE_CLIENT_SECRET is not configured in settings.")
                return False, "Server configuration error"
            
            # 1. Prepare data for token exchange
            token_data = {
                'code': authorization_code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            [attachment_1](attachment)
            
            # 2. Get tokens from Google
            token_response = requests.post(TOKEN_URL, data=token_data)
            
            if token_response.status_code != 200:
                error_detail = token_response.json().get('error_description', token_response.text)
                logger.error(f"Token exchange failed (Code: {token_response.status_code}): {error_detail}")
                return False, f"Failed to exchange authorization code: {error_detail}"
            
            tokens = token_response.json()
            id_token_str = tokens.get('id_token')
            
            # 3. Verify the resulting ID Token
            if not id_token_str:
                return False, "Token exchange succeeded but no ID token was returned."
                
            # Reuse the dedicated verification logic for the received ID token
            is_valid, data_or_error = GoogleAuth.verify_id_token(id_token_str)
            
            if not is_valid:
                logger.error(f"ID Token received after exchange failed verification: {data_or_error}")
                return False, f"Authentication failed after exchange: {data_or_error}"
            
            # Success: Return the verified user data
            logger.info(f"Successfully exchanged code for user: {data_or_error.get('email')}")
            return True, data_or_error
                
        except Exception as e:
            logger.error(f"Unexpected error during code exchange: {str(e)}", exc_info=True)
            return False, "Error exchanging authorization code"

            

class AppleAuth:
    
    APPLE_PUBLIC_KEY_URL = "https://appleid.apple.com/auth/keys"
    APPLE_ISSUER = "https://appleid.apple.com"
    
    @staticmethod
    def get_apple_public_key(token: str) -> Optional[str]:
        """
        Fetch Apple's public keys and return the matching key for the token
        
        Args:
            token: Apple identity token
            
        Returns:
            Public key string or None
        """
        try:
            # Decode token header to get the key id (kid)
            headers = jwt.get_unverified_header(token)
            kid = headers.get('kid')
            
            # Fetch Apple's public keys
            response = requests.get(AppleAuth.APPLE_PUBLIC_KEY_URL)
            apple_keys = response.json()
            
            # Find the matching key
            for key in apple_keys.get('keys', []):
                if key.get('kid') == kid:
                    # Convert JWK to PEM format
                    public_key = RSAAlgorithm.from_jwk(key)
                    return public_key
            
            logger.error(f"No matching Apple public key found for kid: {kid}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Apple public key: {str(e)}")
            return None
    
    @staticmethod
    def verify_apple_token(token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify Apple identity token and extract user information
        
        Args:
            token: Apple identity token from the client
            
        Returns:
            Tuple of (success: bool, user_info: dict or error_message: str)
        """
        try:
            # Get Apple's public key
            public_key = AppleAuth.get_apple_public_key(token)
            if not public_key:
                return False, "Could not retrieve Apple public key"
            
            # Verify and decode the token
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=settings.APPLE_CLIENT_ID,
                issuer=AppleAuth.APPLE_ISSUER
            )
            
            # Extract user information
            user_data = {
                'email': decoded.get('email'),
                'email_verified': decoded.get('email_verified', False),
                'sub': decoded.get('sub'),
            }
            
            logger.info(f"Successfully verified Apple token for email: {user_data['email']}")
            return True, user_data
            
        except jwt.ExpiredSignatureError:
            logger.error("Apple token has expired")
            return False, "Token has expired"
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid Apple token: {str(e)}")
            return False, "Invalid token"
        except Exception as e:
            logger.error(f"Unexpected error during Apple authentication: {str(e)}")
            return False, "Authentication failed"


def get_or_create_social_user(provider: str, user_data: Dict, extra_data: Optional[Dict] = None):
    
    email = user_data.get('email')
    
    if not email:
        raise ValueError("Email is required for social authentication")
    
    try:
        # Try to get existing user
        user = Profile.objects.get(email=email)
        logger.info(f"Existing user found for email: {email}")
        
        # Update email verification status if needed
        if not user.email_verified and user_data.get('email_verified'):
            user.email_verified = True
            user.save()
        
        return user, False
        
    except Profile.DoesNotExist:
        # Create new user
        with db_transaction.atomic():
            logger.info(f"Creating new user for email: {email}")
            
            # Extract names
            if provider == 'google':
                surname = user_data.get('family_name', '')
                other_names = user_data.get('given_name', '')
            elif provider == 'apple':
                # For Apple, names come from extra_data on first sign-in
                if extra_data:
                    name = extra_data.get('name', {})
                    surname = name.get('lastName', '')
                    other_names = name.get('firstName', '')
                else:
                    surname = ''
                    other_names = ''
            else:
                surname = ''
                other_names = ''
            
            # If no names provided, use email username
            if not other_names and not surname:
                other_names = email.split('@')[0]
            
            # Create user
            user = Profile.objects.create(
                email=email,
                surname=surname,
                other_names=other_names,
                email_verified=user_data.get('email_verified', True),
                role='user',
                is_active=True
            )
            
            # Set unusable password for social login users
            user.set_unusable_password()
            user.save()
            
            # Create wallet for the new user
            try:
                Wallet.objects.create(user=user)
                logger.info(f"Successfully created wallet for: {email}")
            except Exception as wallet_error:
                logger.error(f"Failed to create wallet for {email}: {str(wallet_error)}")
                # Don't fail user creation if wallet creation fails
                # The wallet can be created later
            
            logger.info(f"Successfully created user and wallet for: {email}")
            return user, True