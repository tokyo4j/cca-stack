#include "llama.h"
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

static std::string
get_reply(llama_context *ctx, const llama_vocab *vocab, llama_sampler *smpl,
        const std::string &prompt)
{
    std::vector<llama_token> tokens(2048);
    int n_tokens = llama_tokenize(vocab, prompt.c_str(), prompt.size(),
            tokens.data(), tokens.size(), true, true);
	int n_past = 0;

    llama_batch batch = llama_batch_init(n_tokens, 0, 1);
    for (int i = 0; i < n_tokens; i++) {
        batch.token[i] = tokens[i];
        batch.pos[i] = n_past++;
        batch.n_seq_id[i] = 1;
        batch.seq_id[i][0] = 0;
    }
    batch.n_tokens = n_tokens;

    if (llama_decode(ctx, batch)) {
        std::cerr << "Failed to decode prompt\n";
        llama_batch_free(batch);
        return "<error>";
    }
    llama_batch_free(batch);

    std::string reply;
    constexpr int MAX_GEN = 50;

    // Generate tokens one by one
    for (int i = 0; i < MAX_GEN; i++) {
        llama_token token = llama_sampler_sample(smpl, ctx, -1);
        if (token == llama_vocab_eos(vocab))
            break;

        char buf[128];
        int n = llama_token_to_piece(vocab, token, buf, sizeof(buf), 0, true);
        if (n > 0)
            reply.append(buf, n);

        // Decode the generated token
        llama_batch gen_batch = llama_batch_init(1, 0, 1);
        gen_batch.n_tokens = 1;
        gen_batch.token[0] = token;
        gen_batch.pos[0] = n_past++;
        gen_batch.n_seq_id[0] = 1;
        gen_batch.seq_id[0][0] = 0;

        if (llama_decode(ctx, gen_batch)) {
            std::cerr << "Decode error\n";
            llama_batch_free(gen_batch);
            break;
        }
        llama_batch_free(gen_batch);
    }

    return reply;
}

int
main(int argc, char **argv)
{
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <model_path> <prompt file>\n";
        return 1;
    }

    const std::string model_path = argv[1];
    const std::string prompt_path = argv[2];

    std::ifstream prompt_ifs(prompt_path);
    if (!prompt_ifs) {
        std::cerr << "Failed to open file: " << prompt_path << "\n";
        return 1;
    }

    std::vector<std::string> prompts;
    std::string line;
    while (std::getline(prompt_ifs, line))
        prompts.push_back(line);

    // Load model
    llama_model_params mparams = llama_model_default_params();
    llama_model *model =
            llama_model_load_from_file(model_path.c_str(), mparams);
    if (!model) {
        std::cerr << "Failed to load model\n";
        return 1;
    }

    llama_context_params cparams = llama_context_default_params();
    const llama_vocab *vocab = llama_model_get_vocab(model);
    llama_sampler *smpl = llama_sampler_init_greedy();

    std::vector<std::string> replies;
    for (const std::string &prompt : prompts) {
        llama_context *ctx = llama_init_from_model(model, cparams);
        replies.push_back(get_reply(ctx, vocab, smpl, prompt));
        llama_free(ctx);
    }

    for (const std::string &reply : replies) {
        std::cout << reply << '\n';
    }

    llama_sampler_free(smpl);
    llama_model_free(model);

    return 0;
}
