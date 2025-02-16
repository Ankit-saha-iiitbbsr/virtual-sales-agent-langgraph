from fastapi import APIRouter, HTTPException
from typing import Dict

from virtual_sales_agent.tools import create_order
from ..models.schemas import MessageRequest, MessageResponse
from database.db_manager import DatabaseManager
from virtual_sales_agent.graph import graph
from datetime import datetime
import uuid
import logging
import time
import json
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()
db_manager = DatabaseManager()

@router.post("/message", response_model=MessageResponse)
# async def send_message(request: MessageRequest):
#     try:
#         message_id = str(uuid.uuid4())
#         customer_id = int(request.customer_id)
#         thread_id = f"thread_{customer_id}_{int(time.time())}"
        
#         logger.info(f"Processing message for customer {customer_id}: {request.message}")
        
#         config = {
#             "configurable": {
#                 "customer_id": customer_id,
#                 "thread_id": thread_id
#             }
#         }
        
#         initial_state = {
#             "messages": [("user", request.message)],
#             "user_info": str(customer_id)
#         }
        
#         result = graph.invoke(initial_state, config=config)
#         logger.info(f"Graph result: {result}")

#         # Extract response based on the result structure
#         response = ""
#         if isinstance(result, dict) and "messages" in result:
#             messages = result["messages"]
#             if isinstance(messages, list):
#                 # Find the last AI message
#                 for msg in reversed(messages):
#                     if hasattr(msg, 'additional_kwargs') and 'tool_calls' in msg.additional_kwargs:
#                         tool_calls = msg.additional_kwargs['tool_calls']
#                         for tool_call in tool_calls:
#                             if tool_call['function']['name'] == 'create_order':
#                                 # Parse the order details
#                                 import json
#                                 order_args = json.loads(tool_call['function']['arguments'])
#                                 products = order_args.get('products', [])
                                
#                                 # Format a nice response
#                                 order_details = []
#                                 for product in products:
#                                     product_name = product.get('ProductName', '')
#                                     quantity = product.get('Quantity', 0)
#                                     order_details.append(f"{quantity} units of {product_name}")
                                
#                                 response = (
#                                     f"I understand you want to order: {', '.join(order_details)}. "
#                                     "Would you like to proceed with this order? "
#                                     "Please confirm by responding with 'yes' or 'no'."
#                                 )
#                                 break
#                         if response:
#                             break

#         if not response:
#             response = (
#                 "I understand you want to place an order. "
#                 "Could you please confirm by responding with 'yes' to proceed or 'no' to cancel?"
#             )

#         timestamp = datetime.now().isoformat()
        
#         # Save to database
#         success = db_manager.save_chat_message(
#             message_id=message_id,
#             customer_id=customer_id,
#             message=request.message,
#             response=response,
#             timestamp=timestamp
#         )
        
#         if not success:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Failed to save chat message"
#             )
        
#         return MessageResponse(
#             message_id=message_id,
#             customer_id=str(customer_id),
#             response=response,
#             timestamp=datetime.fromisoformat(timestamp)
#         )
        
#     except Exception as e:
#         logger.error(f"Error processing message: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing message: {str(e)}"
#         ) 

@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    try:
        message_id = str(uuid.uuid4())
        customer_id = int(request.customer_id)
        thread_id = f"thread_{customer_id}_{int(time.time())}"
        timestamp = datetime.now().isoformat()
        response = ""  # Initialize response variable

        # Check if there's a pending order
        pending_order = db_manager.get_pending_order(customer_id)
        
        if pending_order and request.message.lower() in ['yes', 'y']:
            # Confirm the order
            order_details = json.loads(pending_order['order_details'])
            
            # Create the order using the stored details
            config = {
                "configurable": {
                    "customer_id": customer_id,
                    "thread_id": thread_id
                }
            }
            
            # Execute the create_order tool directly
            order_result = create_order(
                products=order_details['products'],
                config=config
            )
            
            if order_result.get('status') == 'success':
                response = (
                    f"Great! Your order has been confirmed. "
                    f"Order ID: {order_result['order_id']}. "
                    f"Total amount: ${order_result['total_amount']:.2f}"
                )
                # Update pending order status
                db_manager.confirm_pending_order(customer_id)
            else:
                response = f"Sorry, there was an issue creating your order: {order_result.get('message')}"
                
        elif pending_order and request.message.lower() in ['no', 'n']:
            # Cancel the pending order
            response = "Order cancelled. Is there anything else I can help you with?"
            
        else:
            # Normal message processing
            config = {
                "configurable": {
                    "customer_id": customer_id,
                    "thread_id": thread_id
                }
            }
            
            initial_state = {
                "messages": [("user", request.message)],
                "user_info": str(customer_id)
            }
            
            result = graph.invoke(initial_state, config=config)
            logger.info(f"Graph result: {result}")  # Add logging
            
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if isinstance(messages, list):
                    for msg in reversed(messages):
                        if hasattr(msg, 'additional_kwargs') and 'tool_calls' in msg.additional_kwargs:
                            tool_calls = msg.additional_kwargs['tool_calls']
                            for tool_call in tool_calls:
                                if tool_call['function']['name'] == 'create_order':
                                    order_args = json.loads(tool_call['function']['arguments'])
                                    
                                    # Save pending order
                                    db_manager.save_pending_order(
                                        customer_id=customer_id,
                                        order_details=json.dumps(order_args),
                                        created_at=timestamp
                                    )
                                    
                                    # Format response
                                    products = order_args.get('products', [])
                                    order_details = []
                                    for product in products:
                                        product_name = product.get('ProductName', '')
                                        quantity = product.get('Quantity', 0)
                                        order_details.append(f"{quantity} units of {product_name}")
                                    
                                    response = (
                                        f"I understand you want to order: {', '.join(order_details)}. "
                                        "Would you like to proceed with this order? "
                                        "Please confirm by responding with 'yes' or 'no'."
                                    )
                                    break
                            if response:
                                break
                    
                    if not response:
                        # Handle regular non-order messages
                        last_message = messages[-1]
                        response = last_message.content if hasattr(last_message, 'content') else str(last_message)

        if not response:
            response = "I'm not sure I understand. Could you please rephrase your request?"

        # Save chat message
        success = db_manager.save_chat_message(
            message_id=message_id,
            customer_id=customer_id,
            message=request.message,
            response=response,
            timestamp=timestamp
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save chat message"
            )

        return MessageResponse(
            message_id=message_id,
            customer_id=str(customer_id),
            response=response,
            timestamp=datetime.fromisoformat(timestamp)
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )