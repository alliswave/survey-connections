(function($) {
    $(document).ready(function() {
        var sourceQuestionSelectElement = document.getElementById("id_source_question");
        if (sourceQuestionSelectElement) {
            sourceQuestionSelectElement.addEventListener("change", function() {
                var selectedSourceQuestionId = sourceQuestionSelectElement.value;
                var fetchUrl = "/admin/surveys/questionflow/fetch-answers/";
                $.ajax({
                    url: fetchUrl,
                    type: "GET",
                    dataType: "json",
                    data: {
                        "source_question": selectedSourceQuestionId
                    },
                    success: function(responseData) {
                        var sourceAnswerSelectElement = document.getElementById("id_source_answer");
                        if (sourceAnswerSelectElement) {
                            sourceAnswerSelectElement.innerHTML = "";
                            var defaultOption = document.createElement("option");
                            defaultOption.value = "";
                            defaultOption.textContent = "---------";
                            sourceAnswerSelectElement.appendChild(defaultOption);
                            responseData.options.forEach(function(answerOption) {
                                var newOption = document.createElement("option");
                                newOption.value = answerOption.id;
                                newOption.textContent = answerOption.text;
                                sourceAnswerSelectElement.appendChild(newOption);
                            });
                        }
                    }
                });
            });
        }
    });
})(django.jQuery); 