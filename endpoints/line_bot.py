import json
from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint
from linebot import LineBotApi
from linebot.models import TextSendMessage

USER_MESSAGES = {}
USER_MODE = {}

class LineBotEndpoint(Endpoint):

    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """

        data = r.get_json()
        
        try:
            # LINEからメッセージを受信
            if data['events'][0]['type'] == 'message':
                # メッセージタイプがテキストの場合
                if data['events'][0]['message']['type'] == 'text':
                    # リプライ用トークン
                    replyToken = data['events'][0]['replyToken']
                    # 受信メッセージ
                    messageText = data['events'][0]['message']['text']
                    dify_response = self.session.app.chat.invoke(
                            app_id=settings["app"]["app_id"],
                            query=messageText,
                            inputs={},
                            response_mode="blocking",
                        )
                    # blocks[0]["elements"][0]["elements"][0]["text"] = dify_response.get("answer")
                    # メッセージを返信（受信メッセージをそのまま返す）
                    LINE_CHANNEL_ACCESS_TOKEN = settings.get("LINE_CHANNEL_ACCESS_TOKEN")
                    LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
                    LINE_BOT_API.reply_message(
                        replyToken,
                        TextSendMessage(
                            text=dify_response.get("answer")
                        )
                    )

        # エラーが起きた場合
        except Exception as e:
            return Response(status=500, response=json.dumps(f'Exception occurred: {e}'))

        return Response(status=200, response=json.dumps('Reply ended normally.'))
