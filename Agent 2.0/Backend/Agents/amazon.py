from uagents import Agent, Context, Model, Protocol
from pydantic import Field
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from ai_engine import UAgentResponse, UAgentResponseType

MYNTRA_Mobile = "6394958060"
MYNTRA_PASSWORD = "YOUR_PASSWORD"
if MYNTRA_Mobile == "YOUR_EMAIL" or MYNTRA_PASSWORD == "YOUR_PASSWORD":
raise Exception("You need to provide your Myntra credentials to use this example")

agent = Agent()

class MyntraCartRequest(Model):
product_url: str = Field(description="The URL of the product to add to the cart on Myntra.")

class Config:
    allow_population_by_field_name = True

async def add_to_cart(product_url: str):
driver = webdriver.Chrome()

try:
    driver.get('https://www.myntra.com/login')

    email_field = driver.find_element_by_name('email')
    email_field.send_keys(MYNTRA_EMAIL)

    password_field = driver.find_element_by_name('password')
    password_field.send_keys(MYNTRA_PASSWORD)
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)  # Adjust time as needed

    driver.get(product_url)

    add_to_cart_button = driver.find_element_by_xpath('//button[contains(text(), "Add to cart")]')
    add_to_cart_button.click()

    time.sleep(5)  # Adjust time as needed
    message = "Item successfully added to the cart."
except Exception as ex:
    message = f"Failed to add item to the cart: {ex}"
finally:
    driver.quit()

return message


myntra_protocol = Protocol("MyntraCartProtocol")

@myntra_protocol.on_message(model=MyntraCartRequest, replies={UAgentResponse})
async def add_to_cart_handler(ctx: Context, sender: str, msg: MyntraCartRequest):
ctx.logger.info(f"Received message from {sender}, session: {ctx.session}")
try:
product_url = msg.product_url
message = await add_to_cart(product_url)
ctx.logger.info(f"message from endpoint: {message}")
await ctx.send(sender, UAgentResponse(message=message, type=UAgentResponseType.FINAL))
except Exception as ex:
ctx.logger.warn(ex)
await ctx.send(sender, UAgentResponse(message=str(ex), type=UAgentResponseType.ERROR))

agent.include(myntra_protocol, publish_manifest=True)

if name == "main":
agent.run()