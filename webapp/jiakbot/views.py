from collections import OrderedDict
from datetime import date

from django.conf import settings
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from bot.jiakbot import JiakBot


class JiakBotView(View):
	"""
	Main View for JiakBot
	"""
	template_name = 'jiakbot/index.html'
	conversation = dict()

	def get(self, request, *args, **kwargs):
		"""
		Initializes JiakBot interface
		"""
		self.conversation = dict()
		clear = request.GET.get('clear', None)
		if clear:
			self.conversation = dict()
		context = {'conversation': self.conversation}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		"""
		AJAX handler for JiakBot
		"""
		user_input = request.POST.get('message')
		jiakbot = JiakBot()
		# Get response
		bot_response = jiakbot.respond(user_input)
		# Add conversation to self.conversation
		if self.conversation:
			self.conversation['user'][max(self.conversation['user'].keys()) + 1] = user_input
			self.conversation['jiakbot'][max(self.conversation['jiakbot'].keys()) + 1] = bot_response
		else:
			self.conversation['user'] = OrderedDict([(1, user_input),])
			self.conversation['jiakbot'] = OrderedDict([(1, bot_response),])
		response = {'response': bot_response}
		return JsonResponse(response)
