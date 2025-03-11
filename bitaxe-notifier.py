import logging
import os
import smtplib
import time
from email.message import EmailMessage

import requests
from dotenv import load_dotenv

load_dotenv(".env")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT = os.getenv("RECIPIENT")

POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", "60"))

NOTIFY_ON_OVERHEAT = bool(os.getenv("NOTIFY_ON_OVERHEAT", "true"))
NOTIFY_ON_NEW_BEST_DIFFICULTY = bool(os.getenv(
    "NOTIFY_ON_NEW_BEST_DIFFICULTY", "true"
))
NOTIFY_ON_NEW_BEST_SESSION_DIFFICULTY = bool(os.getenv(
    "NOTIFY_ON_NEW_BEST_SESSION_DIFFICULTY", "true"
))


def check_env_vars() -> None:
    REQUIRED_VARS = [
        "BITAXE_1_IP",
        "GMAIL_USER",
        "GMAIL_APP_PASSWORD",
        "RECIPIENT"
    ]
    missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing_vars == REQUIRED_VARS:
        logger.critical(
            'Missing or empty ".env" file. Make sure to copy and rename ".env.example" to ".env" and replace the values with your own.'
        )
        exit(1)
    elif missing_vars:
        logger.critical(
            f"Missing required environment variable(s): {', '.join(missing_vars)}"
        )
        exit(1)


def get_bitaxe_configs() -> list[dict[str, str]]:
    bitaxes: list[dict[str, str]] = []

    i = 1
    while True:
        ip_key = f"BITAXE_{i}_IP"
        name_key = f"BITAXE_{i}_NAME"

        ip = os.getenv(ip_key)
        if not ip:
            break

        name = os.getenv(name_key, f"Bitaxe {i}")
        bitaxes.append({"ip": ip, "name": name})
        i += 1

    return bitaxes


def get_system_info(ip: str) -> dict[str, str | int] | None:
    try:
        response = requests.get(
            f"http://{ip}/api/system/info",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.error(
            f"API request failed for {ip}: Connection refused. Please check the IP address."
        )
        return None
    except requests.RequestException as e:
        logger.error(f"API request failed for {ip}: {str(e)}")
        return None


def send_email(subject: str, body: str) -> None:
    msg = EmailMessage()
    msg['from'] = GMAIL_USER
    msg['to'] = RECIPIENT
    msg['subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)  # type: ignore
            server.send_message(msg)
        logger.info(f"Sent email: {subject}")
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Failed to send email: Gmail user or app password not accepted."
        )
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")


def get_bitaxe_states(bitaxes: list[dict[str, str]]) -> dict[str, dict[str, str | int]]:
    bitaxe_states: dict[str, dict[str, str | int]] = {}
    for bitaxe in bitaxes:
        ip = bitaxe['ip']
        name = bitaxe['name']

        data = get_system_info(ip)
        if not data:
            logger.critical(
                f"Failed to get initial system info for {name}. Exiting."
            )
            exit(1)

        logger.info(f"{name} - Initial best difficulty: {data['bestDiff']}")
        logger.info(
            f"{name} - Initial best session difficulty: {data['bestSessionDiff']}"
        )

        bitaxe_states[ip] = {
            "overheat_mode": data['overheat_mode'],
            "bestDiff": data['bestDiff'],
            "bestSessionDiff": data['bestSessionDiff']
        }

    return bitaxe_states


def main() -> None:
    logger.info("Starting Bitaxe Notifier.")

    check_env_vars()

    bitaxes = get_bitaxe_configs()

    logger.info(f"Monitoring {len(bitaxes)} Bitaxe(s)")

    bitaxe_states = get_bitaxe_states(bitaxes)

    try:
        while True:
            time.sleep(POLLING_INTERVAL_SECONDS)

            for bitaxe in bitaxes:
                ip = bitaxe['ip']
                name = bitaxe['name']
                state = bitaxe_states[ip]

                data = get_system_info(ip)
                if not data:
                    logger.warning(
                        f"Failed to get system info for {name}, will retry next interval."
                    )
                    continue

                if data['overheat_mode'] and not state['overheat_mode'] and NOTIFY_ON_OVERHEAT:
                    logger.warning(f"{name} - Overheat mode activated.")
                    send_email(
                        f"{name} Overheated",
                        f"Overheat mode is active on {name}."
                    )
                    state['overheat_mode'] = True
                elif not data['overheat_mode'] and state['overheat_mode']:
                    logger.info(f"{name} - Overheat mode deactivated.")
                    state['overheat_mode'] = False

                if data['bestDiff'] != state['bestDiff'] and NOTIFY_ON_NEW_BEST_DIFFICULTY:
                    logger.info(
                        f"{name} - New best difficulty: {data['bestDiff']}"
                    )
                    send_email(
                        "New Best Difficulty",
                        f"{name} achieved {data['bestDiff']} all-time best"
                    )
                    state['bestDiff'] = data['bestDiff']
                elif (
                    data['bestSessionDiff'] != state['bestSessionDiff']
                    and data['bestSessionDiff'] != "0"
                    and NOTIFY_ON_NEW_BEST_SESSION_DIFFICULTY
                ):
                    logger.info(
                        f"{name} - New best session difficulty: {data['bestSessionDiff']}"
                    )
                    send_email(
                        "New Best Session Difficulty",
                        f"{name} achieved {data['bestSessionDiff']} since system boot"
                    )
                    state['bestSessionDiff'] = data['bestSessionDiff']

    except KeyboardInterrupt:
        logger.info("Stopped by user.")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bitaxe-notifier.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("bitaxe-notifier")

    main()
